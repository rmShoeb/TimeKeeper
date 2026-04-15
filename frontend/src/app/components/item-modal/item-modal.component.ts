import { Component, signal, input, output, computed, effect, ElementRef, viewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TrackingItem } from '../../models/tracking-item.model';
import { Category } from '../../models/category.model';
import flatpickr from 'flatpickr';
import type { Instance } from 'flatpickr/dist/types/instance';

export interface ItemFormData {
  title: string;
  category_id: number | null;
  reminder_date: string;
  description: string;
}

@Component({
  selector: 'app-item-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './item-modal.component.html',
  styleUrls: ['./item-modal.component.css']
})
export class ItemModalComponent implements AfterViewInit {
  dateInput = viewChild<ElementRef<HTMLInputElement>>('dateInput');

  private flatpickrInstance: Instance | null = null;
  // Inputs
  visible = input.required<boolean>();
  mode = input.required<'create' | 'edit' | 'recreate'>();
  categories = input.required<Category[]>();
  formData = input.required<ItemFormData>();

  // Outputs
  save = output<ItemFormData>();
  cancel = output<void>();
  validationError = output<string>();

  // Computed minimum date (today's date in YYYY-MM-DD format)
  minDate = computed(() => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  });

  constructor() {
    // Effect to reinitialize Flatpickr when modal becomes visible
    effect(() => {
      if (this.visible() && this.dateInput()) {
        setTimeout(() => this.initializeFlatpickr(), 0);
      }
    });
  }

  ngAfterViewInit(): void {
    this.initializeFlatpickr();
  }

  ngOnDestroy(): void {
    if (this.flatpickrInstance) {
      this.flatpickrInstance.destroy();
    }
  }

  private initializeFlatpickr(): void {
    const dateInputEl = this.dateInput()?.nativeElement;
    if (!dateInputEl) return;

    // Destroy existing instance if any
    if (this.flatpickrInstance) {
      this.flatpickrInstance.destroy();
    }

    // Initialize Flatpickr
    this.flatpickrInstance = flatpickr(dateInputEl, {
      minDate: 'today',
      dateFormat: 'Y-m-d',
      altInput: true,
      altFormat: 'F j, Y',
      defaultDate: this.formData().reminder_date || undefined,
      onChange: (selectedDates, dateStr) => {
        // Update form data when date is selected
        const formData = this.formData();
        formData.reminder_date = dateStr;
      },
      onReady: (selectedDates, dateStr, instance) => {
        // Add some custom styling via class
        instance.calendarContainer.classList.add('flatpickr-modern');
      }
    });
  }

  onSave(): void {
    // Validate that the date is not in the past
    const dateStr = this.formData().reminder_date;
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time to compare dates only

    // Parse date string as local date (YYYY-MM-DD)
    const [year, month, day] = dateStr.split('-').map(Number);
    const selectedDate = new Date(year, month - 1, day); // month is 0-indexed

    if (selectedDate < today) {
      this.validationError.emit('Reminder date cannot be in the past. Please select today or a future date.');
      return;
    }

    this.save.emit(this.formData());
  }

  onCancel(): void {
    this.cancel.emit();
  }

  validateDate(): void {
    const dateStr = this.formData().reminder_date;
    if (!dateStr) return;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Parse date string as local date (YYYY-MM-DD)
    const [year, month, day] = dateStr.split('-').map(Number);
    const selectedDate = new Date(year, month - 1, day); // month is 0-indexed

    if (selectedDate < today) {
      this.validationError.emit('Reminder date cannot be in the past. Please select today or a future date.');
    }
  }

  getModalTitle(): string {
    const modeValue = this.mode();
    if (modeValue === 'create') return 'Create New Reminder';
    if (modeValue === 'edit') return 'Edit Reminder';
    return 'Recreate Reminder';
  }

  getActionButtonText(): string {
    const modeValue = this.mode();
    if (modeValue === 'create') return 'Create';
    if (modeValue === 'edit') return 'Update';
    return 'Recreate';
  }
}
