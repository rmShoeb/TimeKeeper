import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Category } from '../models/category.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CategoryService {
  private readonly API_URL = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${this.API_URL}/categories`);
  }

  createCategory(name: string): Observable<Category> {
    return this.http.post<Category>(`${this.API_URL}/categories`, { name });
  }

  updateCategory(id: number, name: string): Observable<Category> {
    return this.http.put<Category>(`${this.API_URL}/categories/${id}`, { name });
  }

  deleteCategory(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.API_URL}/categories/${id}`);
  }
}
