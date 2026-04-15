import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap, switchMap } from 'rxjs/operators';
import { User } from '../models/user.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'jwt_token';
  private readonly API_URL = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    // Check if user is already logged in
    if (this.isAuthenticated()) {
      this.loadCurrentUser();
    }
  }

  requestOtp(email: string): Observable<{ message: string; email: string }> {
    return this.http.post<{ message: string; email: string }>(
      `${this.API_URL}/auth/request-otp`,
      { email }
    );
  }

  verifyOtp(email: string, otpCode: string): Observable<User> {
    return this.http.post<{ access_token: string; token_type: string }>(
      `${this.API_URL}/auth/verify-otp`,
      { email, otp_code: otpCode }
    ).pipe(
      tap(response => {
        // Save token first
        sessionStorage.setItem(this.TOKEN_KEY, response.access_token);
      }),
      // Then fetch and return user info
      switchMap(() => this.http.get<User>(`${this.API_URL}/auth/me`)),
      tap(user => {
        // Update current user subject
        this.currentUserSubject.next(user);
      })
    );
  }

  private loadCurrentUser(): void {
    this.http.get<User>(`${this.API_URL}/auth/me`).subscribe({
      next: (user) => this.currentUserSubject.next(user),
      error: () => this.logout()
    });
  }

  getToken(): string | null {
    return sessionStorage.getItem(this.TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  logout(): void {
    sessionStorage.removeItem(this.TOKEN_KEY);
    this.currentUserSubject.next(null);
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }
}
