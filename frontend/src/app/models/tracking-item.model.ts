import { Category } from './category.model';

export interface TrackingItem {
  id: number;
  user_id: number;
  title: string;
  category_id: number;
  category?: Category;
  reminder_date: string;
  description: string | null;
  is_done: boolean;
  created_at: string;
}

export interface TrackingItemCreate {
  title: string;
  category_id: number;
  reminder_date: string;
  description?: string;
}

export interface TrackingItemUpdate {
  title?: string;
  category_id?: number;
  reminder_date?: string;
  description?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  page_size: number;
}
