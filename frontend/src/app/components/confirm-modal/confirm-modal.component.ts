import { Component, input, output, signal } from '@angular/core';

@Component({
  selector: 'app-confirm-modal',
  standalone: true,
  templateUrl: './confirm-modal.component.html',
  styleUrl: './confirm-modal.component.css'
})
export class ConfirmModalComponent {
  visible = input.required<boolean>();
  title = input.required<string>();
  message = input.required<string>();
  confirmText = input<string>('Confirm');
  cancelText = input<string>('Cancel');
  confirmButtonClass = input<string>('btn-danger');

  confirm = output<void>();
  cancel = output<void>();
}
