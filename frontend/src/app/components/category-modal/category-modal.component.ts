import { Component, input, output, model } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Category } from '../../models/category.model';

@Component({
  selector: 'app-category-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './category-modal.component.html',
  styleUrls: ['./category-modal.component.css']
})
export class CategoryModalComponent {
  // Inputs
  visible = input.required<boolean>();
  predefinedCategories = input.required<Category[]>();
  customCategories = input.required<Category[]>();

  // Two-way binding for new category name
  newCategoryName = model('');

  // Outputs
  close = output<void>();
  createCategory = output<string>();
  deleteCategory = output<number>();

  onClose(): void {
    this.close.emit();
  }

  onCreate(): void {
    const name = this.newCategoryName();
    if (name) {
      this.createCategory.emit(name);
    }
  }

  onDelete(id: number): void {
    this.deleteCategory.emit(id);
  }
}
