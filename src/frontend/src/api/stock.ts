// @ts-nocheck
import apiClient from './client';
import { mockApiService } from './mockService';
import type {
  Stock,
  StockCreate,
  StockUpdate,
  StockLocation,
  Category,
  Store,
  StockHistory,
  CommittedStock,
  StockReservation,
  StockTransfer,
  Stocktake,
  StocktakeForm,
  PurchaseOrder,
  PurchaseOrderForm,
  PaginatedResponse,
  StockFilters,
  Manufacturer,
  DeliveryPerson,
  Invoice,
  InvoiceForm,
  Payment,
  PaymentForm,
} from '@/types/stock';

const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true';

export class StockAPI {
  // Stock CRUD operations
  async getStocks(params?: StockFilters): Promise<PaginatedResponse<Stock>> {
    if (isDemoMode) return mockApiService.getStocks(params);
    return apiClient.get('/stock/', params);
  }

  async getStockList(params?: any): Promise<PaginatedResponse<Stock>> {
    return apiClient.get('/stock/', params);
  }

  async getStock(id: number): Promise<Stock> {
    return apiClient.get(`/stock/${id}/`);
  }

  async createStock(data: StockCreate): Promise<Stock> {
    return apiClient.post('/stock/', data);
  }

  async updateStock(id: number, data: StockUpdate): Promise<Stock> {
    return apiClient.patch(`/stock/${id}/`, data);
  }

  async deleteStock(id: number): Promise<void> {
    return apiClient.delete(`/stock/${id}/`);
  }

  // Stock location operations
  async updateStockLocation(id: number, data: { aisle?: string }): Promise<StockLocation> {
    return apiClient.patch(`/stock-locations/${id}/`, data);
  }

  // Stock operations
  async issueStock(id: number, data: {
    quantity: number;
    issued_by?: string;
    note?: string;
    location_id?: number;
  }): Promise<{ message: string; new_quantity: number; available_for_sale: number }> {
    return apiClient.post(`/stock/${id}/issue/`, data);
  }

  async receiveStock(id: number, data: {
    quantity: number;
    received_by?: string;
    note?: string;
    location_id?: number;
    aisle?: string;
  }): Promise<{ message: string; new_quantity: number; available_for_sale: number }> {
    return apiClient.post(`/stock/${id}/receive/`, data);
  }

  async reserveStock(id: number, data: {
    quantity: number;
    reservation_type: string;
    customer_name?: string;
    customer_phone?: string;
    reason: string;
    expires_at: string;
  }): Promise<StockReservation> {
    return apiClient.post(`/stock/${id}/reserve/`, data);
  }

  async commitStock(id: number, data: {
    quantity: number;
    customer_order_number: string;
    deposit_amount: number;
    customer_name: string;
    customer_phone?: string;
    customer_email?: string;
    notes?: string;
  }): Promise<CommittedStock> {
    return apiClient.post(`/stock/${id}/commit/`, data);
  }

  // Stock information
  async getStockHistory(id: number): Promise<StockHistory[]> {
    return apiClient.get(`/stock/${id}/history/`);
  }

  async getStockLocations(id: number): Promise<any[]> {
    return apiClient.get(`/stock/${id}/locations/`);
  }

  async getLowStock(): Promise<PaginatedResponse<Stock>> {
    return apiClient.get('/stock/low-stock/');
  }

  async getStockByCondition(): Promise<any[]> {
    return apiClient.get('/stock/by-condition/');
  }

  // Categories
  async getCategories(): Promise<PaginatedResponse<Category>> {
    return apiClient.get('/categories/');
  }

  async createCategory(data: { group: string }): Promise<Category> {
    return apiClient.post('/categories/', data);
  }

  // Stores/Locations
  async getStores(): Promise<PaginatedResponse<Store>> {
    if (isDemoMode) return mockApiService.getStores();
    return apiClient.get('/stores/');
  }

  async getLocations(): Promise<string[]> {
    return apiClient.get('/locations/');
  }

  // Manufacturers
  async getManufacturers(params?: any): Promise<PaginatedResponse<Manufacturer>> {
    return apiClient.get('/manufacturers/', params);
  }

  async getManufacturer(id: number): Promise<Manufacturer> {
    return apiClient.get(`/manufacturers/${id}/`);
  }

  // Delivery Persons
  async getDeliveryPersons(params?: any): Promise<PaginatedResponse<DeliveryPerson>> {
    return apiClient.get('/delivery-persons/', params);
  }

  async getDeliveryPerson(id: number): Promise<DeliveryPerson> {
    return apiClient.get(`/delivery-persons/${id}/`);
  }

  // Stock History
  async getAllStockHistory(params?: any): Promise<PaginatedResponse<StockHistory>> {
    return apiClient.get('/stock-history/', params);
  }

  // Committed Stock
  async getCommittedStock(params?: any): Promise<PaginatedResponse<CommittedStock>> {
    return apiClient.get('/committed-stock/', params);
  }

  async fulfillCommitment(id: number): Promise<{ message: string; commitment: CommittedStock }> {
    return apiClient.post(`/committed-stock/${id}/fulfill/`);
  }

  // Stock Reservations
  async getReservations(params?: any): Promise<PaginatedResponse<StockReservation>> {
    return apiClient.get('/reservations/', params);
  }

  async getReservation(id: number): Promise<StockReservation> {
    return apiClient.get(`/reservations/${id}/`);
  }

  async createReservation(data: any): Promise<StockReservation> {
    return apiClient.post('/reservations/', data);
  }

  async fulfillReservation(id: number): Promise<{ message: string; reservation: StockReservation }> {
    return apiClient.post(`/reservations/${id}/fulfill/`);
  }

  async cancelReservation(id: number): Promise<{ message: string; reservation: StockReservation }> {
    return apiClient.post(`/reservations/${id}/cancel/`);
  }

  async getActiveReservations(): Promise<PaginatedResponse<StockReservation>> {
    return apiClient.get('/reservations/active/');
  }

  async getExpiredReservations(): Promise<StockReservation[]> {
    return apiClient.get('/reservations/expired/');
  }

  // Stock Transfers
  async getTransfers(params?: any): Promise<PaginatedResponse<StockTransfer>> {
    return apiClient.get('/transfers/', params);
  }

  async getTransfer(id: number): Promise<StockTransfer> {
    return apiClient.get(`/transfers/${id}/`);
  }

  async createTransfer(data: any): Promise<StockTransfer> {
    return apiClient.post('/transfers/', data);
  }

  async approveTransfer(id: number): Promise<{ message: string; transfer: StockTransfer }> {
    return apiClient.post(`/transfers/${id}/approve/`);
  }

  async completeTransfer(id: number): Promise<{ message: string; transfer: StockTransfer }> {
    return apiClient.post(`/transfers/${id}/complete/`);
  }

  async collectTransfer(id: number): Promise<{ message: string; transfer: StockTransfer }> {
    return apiClient.post(`/transfers/${id}/collect/`);
  }

  async dispatchTransfer(id: number): Promise<{ message: string; transfer: StockTransfer }> {
    return apiClient.post(`/transfers/${id}/dispatch/`);
  }

  async cancelTransfer(id: number): Promise<{ message: string; transfer: StockTransfer }> {
    return apiClient.post(`/transfers/${id}/cancel/`);
  }

  async getPendingTransfers(): Promise<PaginatedResponse<StockTransfer>> {
    return apiClient.get('/transfers/pending/');
  }

  async getAwaitingCollectionTransfers(): Promise<PaginatedResponse<StockTransfer>> {
    return apiClient.get('/transfers/awaiting-collection/');
  }

  // Stocktakes (Stock Audits)
  async getStocktakes(params?: any): Promise<PaginatedResponse<Stocktake>> {
    if (isDemoMode) return mockApiService.getStocktakes(params);
    return apiClient.get('/stock-audits/', params);
  }

  async getStocktake(id: number): Promise<Stocktake> {
    if (isDemoMode) return mockApiService.getStocktake(id);
    return apiClient.get(`/stock-audits/${id}/`);
  }

  async createStocktake(data: StocktakeForm): Promise<Stocktake> {
    if (isDemoMode) return mockApiService.createStocktake(data);
    return apiClient.post('/stock-audits/', data);
  }

  async updateStocktake(id: number, data: Partial<StocktakeForm>): Promise<Stocktake> {
    return apiClient.patch(`/stock-audits/${id}/`, data);
  }

  async deleteStocktake(id: number): Promise<void> {
    return apiClient.delete(`/stock-audits/${id}/`);
  }

  async startStocktake(id: number): Promise<{ message: string; audit: Stocktake }> {
    if (isDemoMode) return mockApiService.startStocktake(id);
    return apiClient.post(`/stock-audits/${id}/start/`);
  }

  async completeStocktake(id: number): Promise<{ message: string; audit: Stocktake }> {
    if (isDemoMode) return mockApiService.completeStocktake(id);
    return apiClient.post(`/stock-audits/${id}/complete/`);
  }

  async cancelStocktake(id: number): Promise<{ message: string; audit: Stocktake }> {
    if (isDemoMode) return mockApiService.cancelStocktake(id);
    return apiClient.post(`/stock-audits/${id}/cancel/`);
  }

  async approveStocktake(id: number): Promise<{ message: string; audit: Stocktake }> {
    return apiClient.post(`/stock-audits/${id}/approve/`);
  }

  async getStocktakeItems(stocktakeId: number, params?: { page?: number; page_size?: number }): Promise<PaginatedResponse<any>> {
    return apiClient.get(`/stock-audits/${stocktakeId}/items/`, params);
  }

  async countStocktakeItem(stocktakeId: number, itemId: number, data: {
    actual_quantity: number;
    notes?: string;
  }): Promise<{ message: string; item: any }> {
    return apiClient.post(`/stock-audits/${stocktakeId}/count_item/`, { item_id: itemId, counted_quantity: data.actual_quantity, notes: data.notes });
  }

  // Purchase Orders
  async getPurchaseOrders(params?: any): Promise<PaginatedResponse<PurchaseOrder>> {
    if (isDemoMode) return mockApiService.getPurchaseOrders(params);
    return apiClient.get('/purchase-orders/', params);
  }

  async getPurchaseOrder(id: number): Promise<PurchaseOrder> {
    if (isDemoMode) return mockApiService.getPurchaseOrder(id);
    return apiClient.get(`/purchase-orders/${id}/`);
  }

  async createPurchaseOrder(data: PurchaseOrderForm): Promise<PurchaseOrder> {
    if (isDemoMode) return mockApiService.createPurchaseOrder(data);
    return apiClient.post('/purchase-orders/', data);
  }

  async updatePurchaseOrder(id: number, data: Partial<PurchaseOrderForm>): Promise<PurchaseOrder> {
    return apiClient.patch(`/purchase-orders/${id}/`, data);
  }

  async deletePurchaseOrder(id: number): Promise<void> {
    return apiClient.delete(`/purchase-orders/${id}/`);
  }

  async sendPurchaseOrder(id: number): Promise<{ message: string; purchase_order: PurchaseOrder }> {
    if (isDemoMode) return mockApiService.sendPurchaseOrder(id);
    return apiClient.post(`/purchase-orders/${id}/send/`);
  }

  async approvePurchaseOrder(id: number): Promise<{ message: string; purchase_order: PurchaseOrder }> {
    if (isDemoMode) return mockApiService.approvePurchaseOrder(id);
    return apiClient.post(`/purchase-orders/${id}/approve/`);
  }

  async receivePurchaseOrder(id: number, data: {
    items: Array<{
      id: number;
      received_quantity: number;
    }>;
    receiving_store_id: number;
    delivery_date?: string;
    notes?: string;
    aisle?: string;
  }): Promise<{ message: string; purchase_order: PurchaseOrder }> {
    return apiClient.post(`/purchase-orders/${id}/receive/`, data);
  }

  async cancelPurchaseOrder(id: number): Promise<{ message: string; purchase_order: PurchaseOrder }> {
    if (isDemoMode) return mockApiService.cancelPurchaseOrder(id);
    return apiClient.post(`/purchase-orders/${id}/cancel/`);
  }

  // Invoice operations
  async getInvoices(params?: any): Promise<PaginatedResponse<Invoice>> {
    return apiClient.get('/invoices/', params);
  }

  async getInvoice(id: number): Promise<Invoice> {
    return apiClient.get(`/invoices/${id}/`);
  }

  async getPurchaseOrderInvoices(poId: number): Promise<Invoice[]> {
    return apiClient.get(`/invoices/?purchase_order=${poId}`);
  }

  async createInvoice(poId: number, data: InvoiceForm): Promise<Invoice> {
    const formData = new FormData();
    formData.append('invoice_number', data.invoice_number);
    formData.append('invoice_date', data.invoice_date);
    formData.append('due_date', data.due_date);
    formData.append('invoice_amount_exc', data.invoice_amount_exc.toString());
    formData.append('gst_amount', data.gst_amount.toString());
    formData.append('invoice_total', data.invoice_total.toString());
    if (data.notes) formData.append('notes', data.notes);
    if (data.invoice_file) formData.append('invoice_file', data.invoice_file);

    // Don't set Content-Type header - axios will set it automatically with the correct boundary
    return apiClient.post(`/purchase-orders/${poId}/create-invoice/`, formData);
  }

  async updateInvoice(id: number, data: Partial<InvoiceForm>): Promise<Invoice> {
    const formData = new FormData();
    if (data.invoice_number) formData.append('invoice_number', data.invoice_number);
    if (data.invoice_date) formData.append('invoice_date', data.invoice_date);
    if (data.due_date) formData.append('due_date', data.due_date);
    if (data.invoice_amount_exc !== undefined) formData.append('invoice_amount_exc', data.invoice_amount_exc.toString());
    if (data.gst_amount !== undefined) formData.append('gst_amount', data.gst_amount.toString());
    if (data.invoice_total !== undefined) formData.append('invoice_total', data.invoice_total.toString());
    if (data.notes) formData.append('notes', data.notes);
    if (data.invoice_file) formData.append('invoice_file', data.invoice_file);

    return apiClient.patch(`/invoices/${id}/`, formData);
  }

  async deleteInvoice(id: number): Promise<void> {
    return apiClient.delete(`/invoices/${id}/`);
  }

  // Payment operations
  async getPayments(invoiceId?: number): Promise<Payment[]> {
    const params = invoiceId ? { invoice: invoiceId } : undefined;
    return apiClient.get('/payments/', params);
  }

  async getPayment(id: number): Promise<Payment> {
    return apiClient.get(`/payments/${id}/`);
  }

  async recordPayment(invoiceId: number, data: PaymentForm): Promise<Payment> {
    const formData = new FormData();
    formData.append('payment_reference', data.payment_reference);
    formData.append('payment_date', data.payment_date);
    formData.append('payment_amount', data.payment_amount.toString());
    formData.append('payment_method', data.payment_method);
    if (data.bank_details) formData.append('bank_details', data.bank_details);
    if (data.notes) formData.append('notes', data.notes);
    if (data.receipt_file) formData.append('receipt_file', data.receipt_file);

    return apiClient.post(`/invoices/${invoiceId}/record-payment/`, formData);
  }

  async updatePayment(id: number, data: Partial<PaymentForm>): Promise<Payment> {
    return apiClient.patch(`/payments/${id}/`, data);
  }

  async deletePayment(id: number): Promise<void> {
    return apiClient.delete(`/payments/${id}/`);
  }
}

// Create singleton instance
export const stockAPI = new StockAPI();
export default stockAPI;