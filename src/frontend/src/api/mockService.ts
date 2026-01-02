// @ts-nocheck
import { mockPurchaseOrders, mockStocktakes, mockStores, mockUser } from './mockData';
import type { PaginatedResponse, PurchaseOrder, Stocktake, Store, AuthUser } from '@/types/stock';

export class MockApiService {
  // Mock delay to simulate network
  private delay(ms: number = 300) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Auth endpoints
  async login(username: string, password: string) {
    await this.delay();
    if (username === 'demo' && password === 'demo') {
      return {
        access: 'mock-access-token',
        refresh: 'mock-refresh-token'
      };
    }
    throw new Error('Invalid credentials. Use demo/demo');
  }

  async getUserProfile(): Promise<AuthUser> {
    await this.delay();
    return mockUser as AuthUser;
  }

  // Purchase Orders
  async getPurchaseOrders(params?: any): Promise<PaginatedResponse<PurchaseOrder>> {
    await this.delay();
    let results = mockPurchaseOrders.results;

    // Simple search filtering
    if (params?.search) {
      const searchLower = params.search.toLowerCase();
      results = results.filter(po =>
        po.po_number.toLowerCase().includes(searchLower) ||
        po.supplier_name.toLowerCase().includes(searchLower)
      );
    }

    // Status filtering
    if (params?.status) {
      results = results.filter(po => po.status === params.status);
    }

    return {
      ...mockPurchaseOrders,
      results,
      count: results.length
    };
  }

  async getPurchaseOrder(id: number): Promise<PurchaseOrder> {
    await this.delay();
    const po = mockPurchaseOrders.results.find(p => p.id === id);
    if (!po) throw new Error('Purchase order not found');
    return po;
  }

  async createPurchaseOrder(data: any): Promise<PurchaseOrder> {
    await this.delay();
    const newPO: PurchaseOrder = {
      id: mockPurchaseOrders.results.length + 1,
      po_number: `PO-2024-${String(mockPurchaseOrders.results.length + 1).padStart(3, '0')}`,
      supplier_name: data.supplier_name,
      supplier_email: data.supplier_email,
      supplier_phone: data.supplier_phone,
      supplier_address: data.supplier_address,
      status: 'draft',
      order_date: new Date().toISOString().split('T')[0],
      expected_delivery_date: data.expected_delivery_date,
      delivery_date: null,
      subtotal: data.items.reduce((sum: number, item: any) => sum + (item.quantity * item.unit_price), 0),
      tax_amount: 0,
      total_amount: 0,
      notes: data.notes,
      created_by: mockUser,
      created_at: new Date().toISOString(),
      sent_at: null,
      received_at: null,
      items: data.items.map((item: any, index: number) => ({
        id: index + 1,
        item_name: item.item_name,
        description: item.description,
        quantity: item.quantity,
        unit_price: item.unit_price,
        total_price: item.quantity * item.unit_price,
        received_quantity: 0,
        notes: item.notes
      })),
      total_items: data.items.length,
      items_received: 0,
      items_pending: data.items.length,
      is_fully_received: false,
      is_overdue: false,
    };

    newPO.tax_amount = newPO.subtotal * 0.1;
    newPO.total_amount = newPO.subtotal + newPO.tax_amount;

    return newPO;
  }

  async sendPurchaseOrder(id: number) {
    await this.delay();
    return { message: 'Purchase order sent successfully', purchase_order: await this.getPurchaseOrder(id) };
  }

  async approvePurchaseOrder(id: number) {
    await this.delay();
    return { message: 'Purchase order approved successfully', purchase_order: await this.getPurchaseOrder(id) };
  }

  async cancelPurchaseOrder(id: number) {
    await this.delay();
    return { message: 'Purchase order cancelled successfully', purchase_order: await this.getPurchaseOrder(id) };
  }

  // Stocktakes
  async getStocktakes(params?: any): Promise<PaginatedResponse<Stocktake>> {
    await this.delay();
    let results = mockStocktakes.results;

    // Simple search filtering
    if (params?.search) {
      const searchLower = params.search.toLowerCase();
      results = results.filter(st =>
        st.name.toLowerCase().includes(searchLower) ||
        (st.description && st.description.toLowerCase().includes(searchLower))
      );
    }

    // Status filtering
    if (params?.status) {
      results = results.filter(st => st.status === params.status);
    }

    return {
      ...mockStocktakes,
      results,
      count: results.length
    };
  }

  async getStocktake(id: number): Promise<Stocktake> {
    await this.delay();
    const stocktake = mockStocktakes.results.find(s => s.id === id);
    if (!stocktake) throw new Error('Stocktake not found');
    return stocktake;
  }

  async createStocktake(data: any): Promise<Stocktake> {
    await this.delay();
    const newStocktake: Stocktake = {
      id: mockStocktakes.results.length + 1,
      name: data.name,
      description: data.description,
      location: data.location_id ? mockStores.results.find(s => s.id === data.location_id) || null : null,
      location_id: data.location_id,
      status: 'planning',
      created_by: mockUser,
      created_at: new Date().toISOString(),
      started_at: null,
      completed_at: null,
      items: [],
      total_items: data.stock_ids?.length || 50,
      items_counted: 0,
      items_pending: data.stock_ids?.length || 50,
      total_variance: 0,
      progress_percentage: 0,
    };

    return newStocktake;
  }

  async startStocktake(id: number) {
    await this.delay();
    return { message: 'Stock audit started successfully', audit: await this.getStocktake(id) };
  }

  async completeStocktake(id: number) {
    await this.delay();
    return { message: 'Stock audit completed successfully', audit: await this.getStocktake(id) };
  }

  async cancelStocktake(id: number) {
    await this.delay();
    return { message: 'Stock audit cancelled successfully', audit: await this.getStocktake(id) };
  }

  // Stores
  async getStores(): Promise<PaginatedResponse<Store>> {
    await this.delay();
    return mockStores as PaginatedResponse<Store>;
  }

  // Stocks (simplified for stocktake creation)
  async getStocks(params?: any) {
    await this.delay();
    return {
      results: [
        { id: 1, item_name: 'Laptop Computer', sku: 'LAPTOP001' },
        { id: 2, item_name: 'Office Chair', sku: 'CHAIR001' },
        { id: 3, item_name: 'Desk Lamp', sku: 'LAMP001' },
      ],
      count: 3
    };
  }
}

export const mockApiService = new MockApiService();