import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ChatDetailsComponent } from './chat-details/chat-details.component';

const routes: Routes = [
  { path: ':id', component: ChatDetailsComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ChatRoutingModule { }
