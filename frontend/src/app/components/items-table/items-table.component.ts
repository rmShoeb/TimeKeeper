import { Component, input, output, model, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TrackingItem } from '../../models/tracking-item.model';

@Component({
  selector: 'app-items-table',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './items-table.component.html',
  styleUrls: ['./items-table.component.css']
})
export class ItemsTableComponent {
  // Inputs
  title = input.required<string>();
  items = input.required<TrackingItem[]>();
  type = input.required<'upcoming' | 'past'>();

  // Pagination inputs
  currentPage = input.required<number>();
  totalPages = input.required<number>();
  pageSize = model.required<number>();

  // Outputs
  edit = output<TrackingItem>();
  delete = output<number>();
  recreate = output<TrackingItem>();
  pageChange = output<number>();

  // Computed
  headerClass = computed(() =>
    this.type() === 'upcoming' ? 'bg-success' : 'bg-secondary'
  );

  badgeClass = computed(() =>
    this.type() === 'upcoming' ? 'bg-info' : 'bg-secondary'
  );

  showPagination = computed(() => this.totalPages() > 1);

  onEdit(item: TrackingItem): void {
    this.edit.emit(item);
  }

  onDelete(id: number): void {
    this.delete.emit(id);
  }

  onRecreate(item: TrackingItem): void {
    this.recreate.emit(item);
  }

  onPageChange(page: number): void {
    this.pageChange.emit(page);
  }

  onPageSizeChange(): void {
    this.pageChange.emit(1); // Reset to first page when page size changes
  }

  getPageNumbers(): number[] {
    return Array.from({ length: Math.min(this.totalPages(), 5) }, (_, i) => i + 1);
  }
}
