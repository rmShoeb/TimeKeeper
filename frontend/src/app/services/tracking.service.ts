import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { TrackingItem, TrackingItemCreate, TrackingItemUpdate, PaginatedResponse } from '../models/tracking-item.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TrackingService {
  private readonly API_URL = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getUpcomingItems(page: number = 1, limit: number = 10): Observable<PaginatedResponse<TrackingItem>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());

    return this.http.get<PaginatedResponse<TrackingItem>>(
      `${this.API_URL}/items/upcoming`,
      { params }
    );
  }

  getPastItems(page: number = 1, limit: number = 10): Observable<PaginatedResponse<TrackingItem>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());

    return this.http.get<PaginatedResponse<TrackingItem>>(
      `${this.API_URL}/items/past`,
      { params }
    );
  }

  createItem(item: TrackingItemCreate): Observable<TrackingItem> {
    return this.http.post<TrackingItem>(`${this.API_URL}/items`, item);
  }

  updateItem(id: number, item: TrackingItemUpdate): Observable<TrackingItem> {
    return this.http.put<TrackingItem>(`${this.API_URL}/items/${id}`, item);
  }

  deleteItem(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.API_URL}/items/${id}`);
  }

  recreateItem(id: number, newDate: string): Observable<TrackingItem> {
    return this.http.post<TrackingItem>(
      `${this.API_URL}/items/${id}/recreate`,
      { reminder_date: newDate }
    );
  }
}
