import { Component, signal, model } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  // Use model() for two-way binding with ngModel
  email = model('');
  otpCode = model('');

  // Use signal() for one-way reactive state
  otpRequested = signal(false);
  loading = signal(false);
  errorMessage = signal('');
  successMessage = signal('');

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onRequestOtp(): void {
    if (!this.email()) return;

    this.loading.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    this.authService.requestOtp(this.email()).subscribe({
      next: () => {
        this.otpRequested.set(true);
        this.successMessage.set(`OTP sent to ${this.email()}. Check your inbox and spam.`);
        this.loading.set(false);
      },
      error: (error) => {
        this.errorMessage.set(error.error?.detail || 'Failed to send OTP. Please try again.');
        this.loading.set(false);
      }
    });
  }

  onVerifyOtp(): void {
    if (!this.email() || !this.otpCode()) return;

    this.loading.set(true);
    this.errorMessage.set('');

    this.authService.verifyOtp(this.email(), this.otpCode()).subscribe({
      next: (user) => {
        // User is now fully loaded and authenticated
        console.log('[LOGIN] User authenticated:', user.email);
        console.log('[LOGIN] Token in storage:', !!sessionStorage.getItem('jwt_token'));

        // Safe to navigate - token and user are both ready
        this.loading.set(false);
        this.router.navigate(['/dashboard']);
      },
      error: (error) => {
        // Keep loading false and show error - do NOT navigate
        this.errorMessage.set(error.error?.detail || 'Invalid or expired OTP. Please try again.');
        this.loading.set(false);
      }
    });
  }

  resetForm(): void {
    this.otpRequested.set(false);
    this.otpCode.update(() => '');
    this.errorMessage.set('');
    this.successMessage.set('');
  }
}
