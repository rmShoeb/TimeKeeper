export interface Category {
  id: number;
  name: string;
  is_predefined: boolean;
  user_id: number | null;
  created_at: string;
}
