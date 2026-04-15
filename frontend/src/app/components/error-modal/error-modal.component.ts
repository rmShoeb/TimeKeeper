import { Component, signal, output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-error-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './error-modal.component.html',
  styleUrls: ['./error-modal.component.css']
})
export class ErrorModalComponent {
  // Signals for modal state
  visible = signal(false);
  title = signal('Error');
  message = signal('');

  // Output event when modal is closed
  closed = output<void>();

  show(title: string, message: string): void {
    this.title.set(title);
    this.message.set(message);
    this.visible.set(true);
  }

  close(): void {
    this.visible.set(false);
    this.closed.emit();
  }
}
