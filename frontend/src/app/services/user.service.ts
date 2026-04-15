import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private readonly API_URL = environment.apiUrl;

  constructor(private http: HttpClient) {}

  requestDeleteAccount(): Observable<{ message: string; email: string }> {
    return this.http.delete<{ message: string; email: string }>(
      `${this.API_URL}/user/delete-account`
    );
  }

  confirmDeleteAccount(otpCode: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(
      `${this.API_URL}/user/confirm-delete`,
      { otp_code: otpCode }
    );
  }
}
