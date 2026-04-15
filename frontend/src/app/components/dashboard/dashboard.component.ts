import { Component, OnInit, signal, computed, viewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { TrackingService } from '../../services/tracking.service';
import { CategoryService } from '../../services/category.service';
import { UserService } from '../../services/user.service';
import { TrackingItem } from '../../models/tracking-item.model';
import { Category } from '../../models/category.model';

// Import child components
import { ItemsTableComponent } from '../items-table/items-table.component';
import { ItemModalComponent, ItemFormData } from '../item-modal/item-modal.component';
import { CategoryModalComponent } from '../category-modal/category-modal.component';
import { DeleteAccountModalComponent } from '../delete-account-modal/delete-account-modal.component';
import { ErrorModalComponent } from '../error-modal/error-modal.component';
import { ConfirmModalComponent } from '../confirm-modal/confirm-modal.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    ItemsTableComponent,
    ItemModalComponent,
    CategoryModalComponent,
    DeleteAccountModalComponent,
    ErrorModalComponent,
    ConfirmModalComponent
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  // View children for direct component access
  errorModal = viewChild.required(ErrorModalComponent);

  // Confirmation modal state
  showConfirmModal = signal(false);
  confirmModalTitle = signal('');
  confirmModalMessage = signal('');
  confirmModalAction = signal<(() => void) | null>(null);

  // User state
  currentUserEmail = signal('');

  // Items state
  upcomingItems = signal<TrackingItem[]>([]);
  pastItems = signal<TrackingItem[]>([]);

  // Pagination state
  upcomingPage = signal(1);
  upcomingPages = signal(1);
  upcomingPageSize = signal(10);

  pastPage = signal(1);
  pastPages = signal(1);
  pastPageSize = signal(10);

  // Categories state
  categories = signal<Category[]>([]);
  predefinedCategories = computed(() => this.categories().filter(c => c.is_predefined));
  customCategories = computed(() => this.categories().filter(c => !c.is_predefined));

  // Item modal state
  showItemModal = signal(false);
  itemModalMode = signal<'create' | 'edit' | 'recreate'>('create');
  itemFormData = signal<ItemFormData>({ title: '', category_id: null, reminder_date: '', description: '' });
  currentItemId = signal<number | null>(null);

  // Category modal state
  showCategoryModal = signal(false);
  newCategoryName = signal('');

  // Delete account modal state
  showDeleteAccountModal = signal(false);
  deleteOtpRequested = signal(false);
  deleteOtpCode = signal('');

  constructor(
    private authService: AuthService,
    private trackingService: TrackingService,
    private categoryService: CategoryService,
    private userService: UserService,
    private router: Router
  ) {}

  ngOnInit(): void {
    console.log('[DASHBOARD] ngOnInit called');
    console.log('[DASHBOARD] Token in storage:', !!sessionStorage.getItem('jwt_token'));

    const user = this.authService.getCurrentUser();
    this.currentUserEmail.set(user?.email || '');
    this.loadCategories();
    this.loadUpcomingItems(1);
    this.loadPastItems(1);
  }

  // Categories
  loadCategories(): void {
    this.categoryService.getCategories().subscribe({
      next: (cats) => this.categories.set(cats),
      error: (error) => this.handleError(error, 'Failed to Load Categories',
        'An unexpected error occurred while loading categories. Please try refreshing the page.')
    });
  }

  createCategory(name: string): void {
    this.categoryService.createCategory(name).subscribe({
      next: () => {
        this.newCategoryName.set('');
        this.loadCategories();
      },
      error: (error) => this.showError('Failed to Create Category',
        this.extractErrorMessage(error, 'An unexpected error occurred while creating the category. Please try again.'))
    });
  }

  deleteCategory(id: number): void {
    this.confirmModalTitle.set('Delete Category');
    this.confirmModalMessage.set('Are you sure you want to delete this category? This action cannot be undone.');
    this.confirmModalAction.set(() => {
      this.categoryService.deleteCategory(id).subscribe({
        next: () => this.loadCategories(),
        error: (error) => this.showError('Failed to Delete Category',
          this.extractErrorMessage(error, 'An unexpected error occurred while deleting the category. Please try again.'))
      });
    });
    this.showConfirmModal.set(true);
  }

  // Upcoming Items
  loadUpcomingItems(page: number): void {
    if (page < 1) return;
    this.trackingService.getUpcomingItems(page, this.upcomingPageSize()).subscribe({
      next: (response) => {
        this.upcomingItems.set(response.items);
        this.upcomingPage.set(response.page);
        this.upcomingPages.set(response.pages);
      },
      error: (error) => this.handleError(error, 'Failed to Load Upcoming Items',
        'An unexpected error occurred while loading upcoming items. Please try refreshing the page.')
    });
  }

  // Past Items
  loadPastItems(page: number): void {
    if (page < 1) return;
    this.trackingService.getPastItems(page, this.pastPageSize()).subscribe({
      next: (response) => {
        this.pastItems.set(response.items);
        this.pastPage.set(response.page);
        this.pastPages.set(response.pages);
      },
      error: (error) => this.handleError(error, 'Failed to Load Past Items',
        'An unexpected error occurred while loading past items. Please try refreshing the page.')
    });
  }

  // Item CRUD operations
  openCreateModal(): void {
    this.itemModalMode.set('create');
    this.itemFormData.set({ title: '', category_id: null, reminder_date: '', description: '' });
    this.currentItemId.set(null);
    this.showItemModal.set(true);
  }

  openEditModal(item: TrackingItem): void {
    this.itemModalMode.set('edit');
    this.itemFormData.set({
      title: item.title,
      category_id: item.category_id,
      reminder_date: item.reminder_date,
      description: item.description || ''
    });
    this.currentItemId.set(item.id);
    this.showItemModal.set(true);
  }

  openRecreateModal(item: TrackingItem): void {
    this.itemModalMode.set('recreate');
    this.itemFormData.set({
      title: item.title,
      category_id: item.category_id,
      reminder_date: '',
      description: item.description || ''
    });
    this.currentItemId.set(item.id);
    this.showItemModal.set(true);
  }

  saveItem(formData: ItemFormData): void {
    const mode = this.itemModalMode();

    // Ensure category_id is not null before sending to API
    if (!formData.category_id) {
      this.showError('Validation Error', 'Please select a category');
      return;
    }

    if (mode === 'create') {
      const createData = {
        title: formData.title,
        category_id: formData.category_id,
        reminder_date: formData.reminder_date,
        description: formData.description
      };
      this.trackingService.createItem(createData).subscribe({
        next: () => {
          this.closeItemModal();
          this.loadUpcomingItems(this.upcomingPage());
        },
        error: (error) => this.showError('Failed to Create Item',
          this.extractErrorMessage(error, 'An unexpected error occurred while creating the item. Please try again.'))
      });
    } else if (mode === 'edit' && this.currentItemId()) {
      const updateData = {
        title: formData.title,
        category_id: formData.category_id,
        reminder_date: formData.reminder_date,
        description: formData.description
      };
      this.trackingService.updateItem(this.currentItemId()!, updateData).subscribe({
        next: () => {
          this.closeItemModal();
          this.loadUpcomingItems(this.upcomingPage());
        },
        error: (error) => this.showError('Failed to Update Item',
          this.extractErrorMessage(error, 'An unexpected error occurred while updating the item. Please try again.'))
      });
    } else if (mode === 'recreate' && this.currentItemId()) {
      this.trackingService.recreateItem(this.currentItemId()!, formData.reminder_date).subscribe({
        next: () => {
          this.closeItemModal();
          this.loadUpcomingItems(this.upcomingPage());
          this.loadPastItems(this.pastPage());
        },
        error: (error) => this.showError('Failed to Recreate Item',
          this.extractErrorMessage(error, 'An unexpected error occurred while recreating the item. Please try again.'))
      });
    }
  }

  closeItemModal(): void {
    this.showItemModal.set(false);
    this.itemFormData.set({ title: '', category_id: null, reminder_date: '', description: '' });
    this.currentItemId.set(null);
  }

  deleteItem(id: number): void {
    this.confirmModalTitle.set('Delete Item');
    this.confirmModalMessage.set('Are you sure you want to delete this tracking item? This action cannot be undone.');
    this.confirmModalAction.set(() => {
      this.trackingService.deleteItem(id).subscribe({
        next: () => this.loadUpcomingItems(this.upcomingPage()),
        error: (error) => this.showError('Failed to Delete Item',
          this.extractErrorMessage(error, 'An unexpected error occurred while deleting the item. Please try again.'))
      });
    });
    this.showConfirmModal.set(true);
  }

  confirmAction(): void {
    const action = this.confirmModalAction();
    if (action) {
      action();
    }
    this.closeConfirmModal();
  }

  closeConfirmModal(): void {
    this.showConfirmModal.set(false);
    this.confirmModalTitle.set('');
    this.confirmModalMessage.set('');
    this.confirmModalAction.set(null);
  }

  // Delete Account
  requestDeleteAccount(): void {
    this.userService.requestDeleteAccount().subscribe({
      next: () => this.deleteOtpRequested.set(true),
      error: (error) => this.showError('Failed to Request Account Deletion',
        this.extractErrorMessage(error, 'An unexpected error occurred while requesting account deletion. Please try again.'))
    });
  }

  confirmDeleteAccount(otpCode: string): void {
    this.userService.confirmDeleteAccount(otpCode).subscribe({
      next: () => {
        this.closeDeleteAccountModal();
        this.showError('Account Deleted',
          'Your account has been permanently deleted. You will be redirected to the login page.');
        setTimeout(() => {
          this.authService.logout();
          this.router.navigate(['/login']);
        }, 3000);
      },
      error: (error) => this.showError('Failed to Delete Account',
        this.extractErrorMessage(error, 'An unexpected error occurred while deleting your account. Please verify the OTP and try again.'))
    });
  }

  closeDeleteAccountModal(): void {
    this.showDeleteAccountModal.set(false);
    this.deleteOtpRequested.set(false);
    this.deleteOtpCode.set('');
  }

  // Error handling
  private handleError(error: any, title: string, message: string): void {
    console.error(`[DASHBOARD] ${title}:`, error);
    if (error.status === 401) {
      this.authService.logout();
      this.router.navigate(['/login']);
    } else {
      this.showError(title, this.extractErrorMessage(error, message));
    }
  }

  /**
   * Extract error message from various error formats
   * - Simple string: "Error message"
   * - Object with detail: { detail: "Error message" }
   * - Validation error array: [{ msg: "Field required", loc: ["body", "field"] }]
   */
  private extractErrorMessage(error: any, fallback: string): string {
    if (!error) return fallback;

    // Check for error.error (HTTP error response)
    const errorBody = error.error || error;

    // Simple string detail
    if (typeof errorBody === 'string') return errorBody;
    if (errorBody.detail && typeof errorBody.detail === 'string') return errorBody.detail;

    // Validation error array (422 Unprocessable Entity)
    if (Array.isArray(errorBody)) {
      const messages = errorBody
        .map((err: any) => {
          const field = err.loc ? err.loc[err.loc.length - 1] : 'field';
          return `${field}: ${err.msg}`;
        })
        .join(', ');
      return messages || fallback;
    }

    return fallback;
  }

  showError(title: string, message: string): void {
    this.errorModal().show(title, message);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
