import { Component, input, output, model, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-delete-account-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './delete-account-modal.component.html',
  styleUrls: ['./delete-account-modal.component.css']
})
export class DeleteAccountModalComponent {
  // Inputs
  visible = input.required<boolean>();
  otpRequested = input.required<boolean>();

  // Two-way binding for OTP code
  otpCode = model('');

  // Outputs
  close = output<void>();
  requestOtp = output<void>();
  confirmDelete = output<string>();

  onClose(): void {
    this.close.emit();
  }

  onRequestOtp(): void {
    this.requestOtp.emit();
  }

  onConfirmDelete(): void {
    this.confirmDelete.emit(this.otpCode());
  }
}
