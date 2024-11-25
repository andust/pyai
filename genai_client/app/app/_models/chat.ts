import { ChatMode } from "../types";

export interface Chat {
  id: string;
  questions: Question[];
}

export interface Question {
  content: string;
  answer: string;
}

export const getClientChat = async (id: string) => {
  return fetch(`${process.env.NEXT_PUBLIC_GENIA_SERIVCE}/api/v1/chat/${id}`, {
    cache: "no-cache",
    credentials: "include",
    method: "get",
  });
};

export const getClientAskChat = async (
  id: string,
  question: string,
  chatMode: ChatMode,
  documentId: string,
) => {
  return fetch(
    `${process.env.NEXT_PUBLIC_GENIA_SERIVCE}/api/v1/rag/ask/${id}`,
    {
      cache: "no-cache",
      credentials: "include",
      method: "post",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content: question, chat_mode: chatMode, document_id: documentId }),
    }
  );
};

export const removeClientChat = async (id: string) => {
  return fetch(`${process.env.NEXT_PUBLIC_GENIA_SERIVCE}/api/v1/chat/${id}`, {
    cache: "no-cache",
    credentials: "include",
    method: "delete",
  });
};