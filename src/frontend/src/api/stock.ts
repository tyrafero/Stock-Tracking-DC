import apiClient from './client';
import { mockApiService } from './mockService';
import type {
  Stock,
  StockCreate,
  StockUpdate,
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
} from '@/types/stock';

const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true';

export class StockAPI {
  // Stock CRUD operations
  async getStocks(params?: StockFilters): Promise<PaginatedResponse<Stock>> {
    if (isDemoMode) return mockApiService.getStocks(params);
    return apiClient.get('/v1/stock/', params);
  }

  async getStockList(params?: any): Promise<PaginatedResponse<Stock>> {
    return apiClient.get('/v1/stock/', params);
  }

  async getStock(id: number): Promise<Stock> {
    return apiClient.get(`/v1/stock/${id}/`);
  }

  async createStock(data: StockCreate): Promise<Stock> {
    return apiClient.post('/v1/stock/', data);
  }

  async updateStock(id: number, data: StockUpdate): Promise<Stock> {
    return apiClient.patch(`/v1/stock/${id}/`, data);
  }

  async deleteStock(id: number): Promise<void> {
    return apiClient.delete(`/v1/stock/${id}/`);
  }

  // Stock operations
  async issueStock(id: number, data: {
    quantity: number;
    issued_by?: string;
    note?: string;
    location_id?: number;
  }): Promise<{ message: string; new_quantity: number; available_for_sale: number }> {
    return apiClient.post(`/v1/stock/${id}/issue/`, data);
  }

  async receiveStock(id: number, data: {
    quantity: number;
    received_by?: string;
    note?: string;
    location_id?: number;
    aisle?: string;
  }): Promise<{ message: string; new_quantity: number; available_for_sale: number }> {
    return apiClient.post(`/v1/stock/${id}/receive/`, data);
  }

  async reserveStock(id: number, data: {
    quantity: number;
    reservation_type: string;
    customer_name?: string;
    customer_phone?: string;
    reason: string;
    expires_at: string;
  }): Promise<StockReservation> {
    return apiClient.post(`/v1/stock/${id}/reserve/`, data);
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
    return apiClient.post(`/v1/stock/${id}/commit/`, data);
  }

  // Stock information
  async getStockHistory(id: number): Promise<StockHistory[]> {
    return apiClient.get(`/v1/stock/${id}/history/`);
  }

  async getStockLocations(id: number): Promise<any[]> {
    return apiClient.get(`/v1/stock/${id}/locations/`);
  }

  async getLowStock(): Promise<PaginatedResponse<Stock>> {
    return apiClient.get('/v1/stock/low-stock/');
  }

  async getStockByCondition(): Promise<any[]> {
    return apiClient.get('/v1/stock/by-condition/');
  }

  // Categories
  async getCategories(): Promise<PaginatedResponse<Category>> {
    return apiClient.get('/v1/categories/');
  }

  async createCategory(data: { group: string }): Promise<Category> {
    return apiClient.post('/v1/categories/', data);
  }

  // Stores/Locations
  async getStores(): Promise<PaginatedResponse<Store>> {
    if (isDemoMode) return mockApiService.getStores();
    return apiClient.get('/v1/stores/');
  }

  async getLocations(): Promise<string[]> {
    return apiClient.get('/v1/locations/');
  }

  // Stock History
  async getAllStockHistory(params?: any): Promise<PaginatedResponse<StockHistory>> {
    return apiClient.get('/v1/stock-history/', params);
  }

  // Committed Stock
  async getCommittedStock(params?: any): Promise<PaginatedResponse<CommittedStock>> {
    return apiClient.get('/v1/committed-stock/', params);
  }

  async fulfillCommitment(id: number): Promise<{ message: string; commitment: CommittedStock }> {
    return apiClient.post(`/v1/committed-stock/${id}/fulfill/`);
  }

  // Stock Reservations
  async getReservations(params?: any): Promise<PaginatedResponse<StockReservation>> {
    return apiClient.get('/v1/reservations/', params);
  }

  async getReservation(id: number): Promise<StockReservation> {
    return apiClient.get(`/v1/reservations/${id}/`);
  }

  async createReservation(data: any): Promise<StockReservation> {
    return apiClient.post('/v1/reservations/', data);
  }

  async fulfillReservation(id: number): Promise<{ message: string; reservation: StockReservation }> {
    return apiClient.post(`/v1/reservations/${id}/fulfill/`);
  }

  async cancelReservation(id: number): Promise<{ message: string; reservation: StockReservation }> {
    return apiClient.post(`/v1/reservations/${id}/cancel/`);
  }

  async getActiveReservations(): Promise<PaginatedResponse<StockReservation>> {
    return apiClient.get('/v1/reservations/active/');
  }

  async getExpiredReservations(): Promise<StockReservation[]> {
    return apiClient.get('/v1/reservations/expired/');
  }

  // Stock Transfers
  async getTransfers(params?: any): Promise<PaginatedResponse<StockTransfer>> {
    return apiClient.get('/v1/transfers/', params);
  }

  async getTransfer(id: number): Promise<StockTransfer> {
    return apiClient.get(`/v1/transfers/${id}/`);
  }

  async createTransfer(data: any): Promise<StockTransfer> {
    return apiClient.post('/v1/transfers/', data);
  }

  async approveTransfer(id: number): Promise<{ message: string; transfer: StockTransfer }> {
    return apiClient.post(`/v1/transfers/${id}/approve/`);
  }

  async completeTransfer(id: number): Promise<{ message: string; transfer: StockTransfer }> {
    return apiClient.post(`/v1/transfers/${id}/complete/`);
  }

  async collectTransfer(id: number): Promise<{ message: string; transfer: StockTransfer }> {
    return apiClient.post(`/v1/transfers/${id}/collect/`);
  }

  async dispatchTransfer(id: number): Promise<{ message: string; transfer: StockTransfer }> {
    return apiClient.post(`/v1/transfers/${id}/dispatch/`);
  }

  async cancelTransfer(id: number): Promise<{ message: string; transfer: StockTransfer }> {
    return apiClient.post(`/v1/transfers/${id}/cancel/`);
  }

  async getPendingTransfers(): Promise<PaginatedResponse<StockTransfer>> {
    return apiClient.get('/v1/transfers/pending/');
  }

  async getAwaitingCollectionTransfers(): Promise<PaginatedResponse<StockTransfer>> {
    return apiClient.get('/v1/transfers/awaiting-collection/');
  }

  // Stocktakes (Stock Audits)
  async getStocktakes(params?: any): Promise<PaginatedResponse<Stocktake>> {
    if (isDemoMode) return mockApiService.getStocktakes(params);
    return apiClient.get('/v1/stock-audits/', params);
  }

  async getStocktake(id: number): Promise<Stocktake> {
    if (isDemoMode) return mockApiService.getStocktake(id);
    return apiClient.get(`/v1/stock-audits/${id}/`);
  }

  async createStocktake(data: StocktakeForm): Promise<Stocktake> {
    if (isDemoMode) return mockApiService.createStocktake(data);
    return apiClient.post('/v1/stock-audits/', data);
  }

  async updateStocktake(id: number, data: Partial<StocktakeForm>): Promise<Stocktake> {
    return apiClient.patch(`/v1/stock-audits/${id}/`, data);
  }

  async deleteStocktake(id: number): Promise<void> {
    return apiClient.delete(`/v1/stock-audits/${id}/`);
  }

  async startStocktake(id: number): Promise<{ message: string; audit: Stocktake }> {
    if (isDemoMode) return mockApiService.startStocktake(id);
    return apiClient.post(`/v1/stock-audits/${id}/start/`);
  }

  async completeStocktake(id: number): Promise<{ message: string; audit: Stocktake }> {
    if (isDemoMode) return mockApiService.completeStocktake(id);
    return apiClient.post(`/v1/stock-audits/${id}/complete/`);
  }

  async cancelStocktake(id: number): Promise<{ message: string; audit: Stocktake }> {
    if (isDemoMode) return mockApiService.cancelStocktake(id);
    return apiClient.post(`/v1/stock-audits/${id}/cancel/`);
  }

  async countStocktakeItem(stocktakeId: number, itemId: number, data: {
    actual_quantity: number;
    notes?: string;
  }): Promise<{ message: string; item: any }> {
    return apiClient.post(`/v1/stock-audits/${stocktakeId}/count_item/`, { item_id: itemId, counted_quantity: data.actual_quantity, notes: data.notes });
  }

  // Purchase Orders
  async getPurchaseOrders(params?: any): Promise<PaginatedResponse<PurchaseOrder>> {
    if (isDemoMode) return mockApiService.getPurchaseOrders(params);
    return apiClient.get('/v1/purchase-orders/', params);
  }

  async getPurchaseOrder(id: number): Promise<PurchaseOrder> {
    if (isDemoMode) return mockApiService.getPurchaseOrder(id);
    return apiClient.get(`/v1/purchase-orders/${id}/`);
  }

  async createPurchaseOrder(data: PurchaseOrderForm): Promise<PurchaseOrder> {
    if (isDemoMode) return mockApiService.createPurchaseOrder(data);
    return apiClient.post('/v1/purchase-orders/', data);
  }

  async updatePurchaseOrder(id: number, data: Partial<PurchaseOrderForm>): Promise<PurchaseOrder> {
    return apiClient.patch(`/v1/purchase-orders/${id}/`, data);
  }

  async deletePurchaseOrder(id: number): Promise<void> {
    return apiClient.delete(`/v1/purchase-orders/${id}/`);
  }

  async sendPurchaseOrder(id: number): Promise<{ message: string; purchase_order: PurchaseOrder }> {
    if (isDemoMode) return mockApiService.sendPurchaseOrder(id);
    return apiClient.post(`/v1/purchase-orders/${id}/send/`);
  }

  async approvePurchaseOrder(id: number): Promise<{ message: string; purchase_order: PurchaseOrder }> {
    if (isDemoMode) return mockApiService.approvePurchaseOrder(id);
    return apiClient.post(`/v1/purchase-orders/${id}/approve/`);
  }

  async receivePurchaseOrder(id: number, data: {
    items: Array<{
      id: number;
      received_quantity: number;
    }>;
    delivery_date?: string;
    notes?: string;
  }): Promise<{ message: string; purchase_order: PurchaseOrder }> {
    return apiClient.post(`/v1/purchase-orders/${id}/receive/`, data);
  }

  async cancelPurchaseOrder(id: number): Promise<{ message: string; purchase_order: PurchaseOrder }> {
    if (isDemoMode) return mockApiService.cancelPurchaseOrder(id);
    return apiClient.post(`/v1/purchase-orders/${id}/cancel/`);
  }
}

// Create singleton instance
export const stockAPI = new StockAPI();
export default stockAPI;