from bson import ObjectId
from typing import Protocol, Sequence

from langchain_core.documents import Document
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorGridFSBucket

from app.constants.file import ProcessState
from app.db.main import db
from app.libs.pdf_reader.main import pdf_to_text
from app.model.file import FileData, FileProtocol, calculate_file_hash


class FileRepositoryProtocol(Protocol):
    async def get_by_hash(self, hash: str) -> FileData | None: ...

    async def upload_files(
        self, files: Sequence[FileProtocol], user_email: str
    ) -> list[Document]: ...

    async def get(self, id: str) -> FileData: ...


class MongoFileRepository:
    def __init__(
        self, collection: AsyncIOMotorCollection, fs: AsyncIOMotorGridFSBucket
    ):
        self.collection = collection
        self.fs = fs

    # TODO change this to get_file_metadata
    async def get_file_content_type(self, id: str) -> str | None:
        result = await self.collection.find_one(
            {"_id": ObjectId(id)}, projection={"metadata.content_type": 1, "_id": 0}
        )

        if result:
            return result["metadata"]["content_type"]

        return

    async def get(self, id: str) -> FileData:
        file_content = await self.get_file_content_type(id)
        grid_out = await self.fs.open_download_stream(ObjectId(id))
        content = await grid_out.read()

        return FileData(content=content, content_type=file_content)

    async def get_by_hash(self, hash: str) -> FileData | None:
        result = await self.collection.find_one(
            {"metadata.hash": hash}, projection={"_id": 1}
        )
        if result:
            return await self.get(result["_id"])

    async def get_many(self) -> list[FileData]:
        # TODO use protocol to abstract this class
        # limit param
        most_recent_three = await self.fs.find().sort("uploadDate", -1).limit(20).to_list()
        print(most_recent_three)
        return [FileData(id=str(a["_id"]), filename=a["filename"], upload_date=a["uploadDate"], content=b"", content_type=a["metadata"]["content_type"]) for a in most_recent_three]

    async def upload_files(
        self, files: Sequence[FileProtocol], user_email: str
    ) -> list[Document]:
        docs = []
        for file in files:
            if not file.filename:
                continue

            file_hash = await calculate_file_hash(file)
            if (await self.get_by_hash(hash=file_hash)) is not None:
                continue

            content = await file.read()

            file_id = await fs.upload_from_stream(
                file.filename or "no-name",
                content,
                metadata={
                    "content_type": file.content_type,
                    "user": user_email,
                    "hash": file_hash,
                    "vectorUploadStatus": ProcessState.PENDING
                },
            )

            if file.content_type == "application/pdf":
                page_content = "\n".join(pdf_to_text(content))
            else:
                page_content = str(content)

            docs.append(
                Document(
                    page_content=page_content,
                    metadata={
                        "file_id": str(file_id),
                        "file_hash": file_hash,
                        "filename": file.filename,
                        "content_type": file.content_type,
                    },
                )
            )

        return docs


fs = AsyncIOMotorGridFSBucket(db)
file_repository = MongoFileRepository(collection=db["fs.files"], fs=fs)
