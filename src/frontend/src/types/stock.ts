// Base types
export interface PaginatedResponse<T> {
  links: {
    next: string | null;
    previous: string | null;
  };
  count: number;
  total_pages: number;
  current_page: number;
  page_size: number;
  results: T[];
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
}

export interface Category {
  id: number;
  group: string;
}

export interface Store {
  id: number;
  name: string;
  designation: 'store' | 'warehouse';
  location: string;
  address?: string;
  email?: string;
  order_email?: string;
  logo_url?: string;
  website_url?: string;
  facebook_url?: string;
  instagram_url?: string;
  abn?: string;
  is_active: boolean;
  initials: string;
}

export interface StockLocation {
  id: number;
  store: Store;
  store_id: number;
  quantity: number;
  aisle?: string;
  last_updated: string;
  created_at: string;
  is_low_stock: boolean;
}

export interface Stock {
  id: number;
  category: Category | null;
  category_id?: number;
  item_name: string;
  sku?: string;
  quantity: number;
  receive_quantity: number;
  received_by?: string;
  issue_quantity: number;
  issued_by?: string;
  committed_quantity: number;
  condition: 'new' | 'demo_unit' | 'bstock' | 'open_box' | 'refurbished';
  condition_display: string;
  location: Store | null;
  location_id?: number;
  aisle?: string;
  note?: string;
  phone_number?: string;
  created_by?: string;
  re_order: number;
  last_updated: string;
  timestamp: string;
  date: string;
  export_to_csv: boolean;
  image_url?: string;
  source_purchase_order?: number;
  opening_stock: number;
  stock_on_hand: number;
  warehouse_name?: string;
  locations: StockLocation[];

  // Computed properties
  total_stock: number;
  committed_stock: number;
  reserved_quantity: number;
  available_for_sale: number;
  is_low_stock: boolean;
  total_across_locations: number;
}

export interface StockCreate {
  category_id?: number;
  item_name: string;
  sku?: string;
  quantity?: number;
  condition?: 'new' | 'demo_unit' | 'bstock' | 'open_box' | 'refurbished';
  location_id?: number;
  aisle?: string;
  note?: string;
  phone_number?: string;
  re_order?: number;
  image_url?: string;
  warehouse_name?: string;
}

export interface StockUpdate extends Partial<StockCreate> {}

export interface StockHistory {
  id: number;
  category: Category | null;
  item_name: string;
  quantity: number;
  receive_quantity: number;
  received_by?: string;
  issue_quantity: number;
  issued_by?: string;
  note?: string;
  phone_number?: string;
  created_by?: string;
  re_order: number;
  last_updated: string | null;
  timestamp: string | null;
}

export interface CommittedStock {
  id: number;
  stock: Stock;
  stock_id: number;
  quantity: number;
  customer_order_number: string;
  deposit_amount: number;
  customer_name: string;
  customer_phone?: string;
  customer_email?: string;
  notes?: string;
  committed_by: User;
  committed_at: string;
  is_fulfilled: boolean;
  fulfilled_at?: string;
}

export interface StockReservation {
  id: number;
  stock: Stock;
  stock_id: number;
  quantity: number;
  reservation_type: 'quote' | 'hold' | 'inspection' | 'transfer_prep' | 'maintenance' | 'other';
  reservation_type_display: string;
  status: 'active' | 'expired' | 'fulfilled' | 'cancelled';
  status_display: string;
  customer_name?: string;
  customer_phone?: string;
  customer_email?: string;
  reference_number?: string;
  reason: string;
  notes?: string;
  reserved_by: User;
  reserved_at: string;
  expires_at: string;
  fulfilled_at?: string;
  cancelled_at?: string;
  fulfilled_by?: User;
  cancelled_by?: User;

  // Computed properties
  is_active: boolean;
  is_expired: boolean;
  can_be_fulfilled: boolean;
  can_be_cancelled: boolean;
  days_until_expiry: number;
}

export interface StockTransfer {
  id: number;
  stock: Stock;
  stock_id: number;
  quantity: number;
  from_location: Store;
  from_location_id: number;
  to_location: Store;
  to_location_id: number;
  from_aisle?: string;
  to_aisle?: string;
  transfer_type: 'restock' | 'customer_collection' | 'general';
  transfer_type_display: string;
  transfer_reason: string;
  customer_name?: string;
  customer_phone?: string;
  notes?: string;
  status: 'pending' | 'in_transit' | 'completed' | 'awaiting_collection' | 'collected' | 'cancelled';
  status_display: string;
  created_by: User;
  approved_by?: User;
  completed_by?: User;
  collected_by?: User;
  created_at: string;
  approved_at?: string;
  completed_at?: string;
  collected_at?: string;

  // Computed properties
  can_be_approved: boolean;
  can_be_completed: boolean;
  can_be_collected: boolean;
  is_pending_collection: boolean;
}

// Filter types
export interface StockFilters {
  search?: string;
  item_name?: string;
  sku?: string;
  category?: number;
  category_name?: string;
  location?: number;
  location_name?: string;
  warehouse_name?: string;
  quantity_min?: number;
  quantity_max?: number;
  quantity_exact?: number;
  available_min?: number;
  available_max?: number;
  condition?: 'new' | 'demo_unit' | 'bstock' | 'open_box' | 'refurbished';
  has_image?: boolean;
  is_low_stock?: boolean;
  has_committed_stock?: boolean;
  has_reserved_stock?: boolean;
  created_after?: string;
  created_before?: string;
  updated_after?: string;
  updated_before?: string;
  zero_quantity?: boolean;
  negative_quantity?: boolean;
  page?: number;
  page_size?: number;
  ordering?: string;
}

// Form types for validation
export interface StockIssueForm {
  quantity: number;
  issued_by?: string;
  note?: string;
  location_id?: number;
}

export interface StockReceiveForm {
  quantity: number;
  received_by?: string;
  note?: string;
  location_id?: number;
  aisle?: string;
}

export interface StockReserveForm {
  quantity: number;
  reservation_type: 'quote' | 'hold' | 'inspection' | 'transfer_prep' | 'maintenance' | 'other';
  customer_name?: string;
  customer_phone?: string;
  customer_email?: string;
  reference_number?: string;
  reason: string;
  notes?: string;
  expires_at: string;
}

export interface StockCommitForm {
  quantity: number;
  customer_order_number: string;
  deposit_amount: number;
  customer_name: string;
  customer_phone?: string;
  customer_email?: string;
  notes?: string;
}

export interface StockTransferForm {
  stock_id: number;
  quantity: number;
  from_location_id: number;
  to_location_id: number;
  from_aisle?: string;
  to_aisle?: string;
  transfer_type: 'restock' | 'customer_collection' | 'general';
  transfer_reason: string;
  customer_name?: string;
  customer_phone?: string;
  notes?: string;
}

// Stocktake types
export interface StocktakeItem {
  id: number;
  audit: number;
  stock: Stock;
  stock_id: number;
  system_quantity: number;
  committed_quantity: number;
  reserved_quantity: number;
  physical_count?: number;
  variance_quantity: number;
  variance_reason?: string;
  variance_notes?: string;
  counted_by?: User;
  count_date?: string;
  adjustment_applied: boolean;
  adjustment_date?: string;
  audit_location?: string;
  audit_aisle?: string;
  created_at: string;
  updated_at: string;

  // Computed properties for compatibility
  expected_quantity?: number;  // Same as system_quantity
  actual_quantity?: number;    // Same as physical_count
  variance?: number;           // Same as variance_quantity
  status?: 'pending' | 'counted' | 'verified' | 'discrepancy';
}

export interface Stocktake {
  id: number;
  audit_reference: string;
  title: string;  // Changed from 'name' to match backend
  description?: string;
  audit_type: 'full' | 'partial' | 'cycle' | 'location' | 'category' | 'spot_check';
  audit_locations?: Store[];
  audit_categories?: Category[];
  location?: Store;  // For backward compatibility
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled' | 'approved';
  planned_start_date: string;
  planned_end_date: string;
  actual_start_date?: string;
  actual_end_date?: string;
  started_at?: string;  // Added for compatibility
  completed_at?: string;  // Added for compatibility
  created_by: User;
  started_by?: User;  // Added for compatibility
  completed_by?: User;  // Added for compatibility
  assigned_auditors?: User[];
  approved_by?: User;
  created_at: string;
  updated_at: string;
  audit_items: StocktakeItem[];

  // Computed properties
  progress_percentage: number;
  total_items_planned: number;
  total_items_counted: number;
  items_with_variances: number;
  total_variance_value: number;
  can_start: boolean;
  can_complete: boolean;

  // Deprecated - for backward compatibility
  items_counted?: number;
  items_pending?: number;
  total_items?: number;
  total_variance?: number;
}

export interface StocktakeForm {
  title: string;  // Changed from 'name' to match backend
  description?: string;
  audit_type?: 'full' | 'partial' | 'cycle' | 'location' | 'category' | 'spot_check';
  planned_start_date: string;  // Required by backend
  planned_end_date: string;    // Required by backend
  audit_location_ids?: number[];  // Changed from single location_id
  audit_category_ids?: number[];
  assigned_auditor_ids?: number[];
}

// Manufacturer and DeliveryPerson types
export interface Manufacturer {
  id: number;
  company_name: string;
  company_email: string;
  additional_email?: string;
  street_address: string;
  city: string;
  country: string;
  region: string;
  postal_code: string;
  company_telephone: string;
  abn?: string;
  created_at: string;
  updated_at: string;
}

export interface DeliveryPerson {
  id: number;
  name: string;
  phone_number: string;
  is_active: boolean;
  created_at: string;
}

// Purchase Order types
export interface PurchaseOrderItem {
  id: number;
  product: string;
  associated_order_number?: string;
  price_inc: number;
  quantity: number;
  discount_percent: number;
  received_quantity: number;
  created_at: string;
  updated_at: string;
}

export interface PurchaseOrder {
  id: number;
  reference_number: string;
  manufacturer: string;
  delivery_person?: string;
  delivery_type?: string;
  creating_store?: string;
  store?: string;
  status: 'draft' | 'sent' | 'confirmed' | 'partially_received' | 'completed' | 'cancelled';
  note_for_manufacturer?: string;
  expected_delivery_date?: string;
  delivery_date?: string;
  created_by: User;
  created_at: string;
  updated_at: string;
  submitted_at?: string;
  sent_at?: string;
  items: PurchaseOrderItem[];
  invoices?: Invoice[];
}

export interface PurchaseOrderForm {
  supplier_name: string;
  supplier_email?: string;
  supplier_phone?: string;
  supplier_address?: string;
  expected_delivery_date?: string;
  notes?: string;
  items: Array<{
    item_name: string;
    description?: string;
    quantity: number;
    unit_price: number;
    notes?: string;
  }>;
}

// Invoice and Payment types
export interface Payment {
  id: number;
  invoice: number;
  payment_reference: string;
  payment_date: string;
  payment_amount: number;
  payment_method: 'bank_transfer' | 'check' | 'cash' | 'credit_card' | 'other';
  payment_status: 'pending' | 'completed' | 'failed' | 'cancelled';
  bank_details?: string;
  notes?: string;
  receipt_file?: string;
  created_by: User;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: number;
  purchase_order: number;
  invoice_number: string;
  invoice_date: string;
  due_date: string;
  invoice_amount_exc: number;
  gst_amount: number;
  invoice_total: number;
  total_paid: number;
  outstanding_amount: number;
  status: 'pending' | 'partially_paid' | 'fully_paid' | 'overdue' | 'disputed' | 'cancelled';
  notes?: string;
  invoice_file?: string;
  created_by: User;
  created_at: string;
  updated_at: string;
  last_payment_date?: string;
  is_overdue: boolean;
  days_overdue: number;
  payment_percentage: number;
  payments?: Payment[];
}

export interface InvoiceForm {
  invoice_number: string;
  invoice_date: string;
  due_date: string;
  invoice_amount_exc: number;
  gst_amount: number;
  invoice_total: number;
  notes?: string;
  invoice_file?: File;
}

export interface PaymentForm {
  payment_reference: string;
  payment_date: string;
  payment_amount: number;
  payment_method: string;
  bank_details?: string;
  notes?: string;
  receipt_file?: File;
}