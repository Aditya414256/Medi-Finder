/**
 * MediFind Unified Frontend Engine & Mock Data Store
 * Provides persistent authentication, medicine search, pharmacy mapping,
 * cart management, order tracking, and role dashboards.
 */

(function () {
  'use strict';

  // ==========================================
  // 1. DEFAULT SEED DATA
  // ==========================================
  const INITIAL_USERS = [
    {
      id: 1,
      email: 'admin@medifind.com',
      password: 'Admin@12345',
      name: 'System Administrator',
      phone: '+1-800-555-0199',
      role: 'admin',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80'
    },
    {
      id: 2,
      email: 'apollo@pharmacy.com',
      password: 'Pharmacy@12345',
      name: 'Dr. Rajiv Sharma',
      phone: '+1-555-0101',
      role: 'pharmacy',
      pharmacyId: 1,
      avatar: 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=100&auto=format&fit=crop&q=80'
    },
    {
      id: 3,
      email: 'medplus@pharmacy.com',
      password: 'Pharmacy@12345',
      name: 'Ananya Gupta',
      phone: '+1-555-0102',
      role: 'pharmacy',
      pharmacyId: 2,
      avatar: 'https://images.unsplash.com/photo-1594824813689-f52f36f6d0f5?w=100&auto=format&fit=crop&q=80'
    },
    {
      id: 4,
      email: 'customer@medifind.com',
      password: 'Customer@12345',
      name: 'John Doe',
      phone: '+1-555-0201',
      role: 'customer',
      address: '742 Evergreen Terrace, Metro City',
      avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop&q=80'
    },
    {
      id: 5,
      email: 'sarah@medifind.com',
      password: 'Customer@12345',
      name: 'Sarah Jenkins',
      phone: '+1-555-0202',
      role: 'customer',
      address: '108 Palm Avenue, Green Valley',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&auto=format&fit=crop&q=80'
    }
  ];

  const INITIAL_PHARMACIES = [
    {
      id: 1,
      name: 'Apollo HealthCare & Pharmacy',
      licenseNumber: 'DL-2024-APL-8821',
      phone: '+1-555-0101',
      email: 'contact@apollopharmacy.example.com',
      address: '14 Central Avenue, Downtown Core',
      city: 'Metro City',
      state: 'Central',
      pincode: '100001',
      latitude: 28.6139,
      longitude: 77.2090,
      rating: 4.8,
      reviewsCount: 142,
      is24x7: true,
      homeDelivery: true,
      status: 'APPROVED',
      openHours: 'Open 24/7',
      image: 'https://images.unsplash.com/photo-1586015555751-63bb77f4322a?w=400&auto=format&fit=crop&q=80'
    },
    {
      id: 2,
      name: 'MedPlus 24x7 Chemist',
      licenseNumber: 'DL-2024-MDP-5532',
      phone: '+1-555-0102',
      email: 'support@medpluschemist.example.com',
      address: '88 West Park Street, Medical Enclave',
      city: 'Metro City',
      state: 'Central',
      pincode: '100002',
      latitude: 28.6250,
      longitude: 77.2180,
      rating: 4.6,
      reviewsCount: 98,
      is24x7: true,
      homeDelivery: true,
      status: 'APPROVED',
      openHours: 'Open 24/7',
      image: 'https://images.unsplash.com/photo-1576602976047-174e57a47881?w=400&auto=format&fit=crop&q=80'
    },
    {
      id: 3,
      name: 'Guardian Life Pharmacy',
      licenseNumber: 'DL-2024-GDN-1109',
      phone: '+1-555-0103',
      email: 'help@guardianlife.example.com',
      address: '204 South Boulevard, Green Valley',
      city: 'Metro City',
      state: 'Central',
      pincode: '100003',
      latitude: 28.5980,
      longitude: 77.2250,
      rating: 4.7,
      reviewsCount: 76,
      is24x7: false,
      homeDelivery: true,
      status: 'APPROVED',
      openHours: '8:00 AM - 11:00 PM',
      image: 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=400&auto=format&fit=crop&q=80'
    },
    {
      id: 4,
      name: 'Wellness Care Meds',
      licenseNumber: 'DL-2024-WLN-9023',
      phone: '+1-555-0104',
      email: 'info@wellnesscaremeds.example.com',
      address: '52 North Ring Road, Tech Park',
      city: 'Metro City',
      state: 'Central',
      pincode: '100004',
      latitude: 28.6320,
      longitude: 77.1950,
      rating: 4.5,
      reviewsCount: 52,
      is24x7: false,
      homeDelivery: false,
      status: 'PENDING',
      openHours: '9:00 AM - 10:00 PM',
      image: 'https://images.unsplash.com/photo-1516549655169-df83a0774514?w=400&auto=format&fit=crop&q=80'
    }
  ];

  const INITIAL_MEDICINES = [
    {
      id: 1,
      name: 'Amoxicillin 500mg',
      genericName: 'Amoxicillin Trihydrate',
      brandName: 'Amoxil / Novamox',
      category: 'Antibiotics',
      dosageForm: 'Capsule',
      strength: '500 mg',
      price: 12.50,
      requiresPrescription: true,
      description: 'Broad-spectrum penicillin antibiotic used to treat bacterial infections of the ear, nose, throat, urinary tract, and skin.',
      sideEffects: 'Nausea, mild rash, stomach upset.',
      manufacturer: 'Cipla Ltd.',
      stocks: { 1: 45, 2: 18, 3: 0 }
    },
    {
      id: 2,
      name: 'Paracetamol 650mg',
      genericName: 'Acetaminophen / Paracetamol',
      brandName: 'Dolo 650 / Calpol',
      category: 'Pain Relief & Fever',
      dosageForm: 'Tablet',
      strength: '650 mg',
      price: 3.20,
      requiresPrescription: false,
      description: 'Analgesic and antipyretic medication used to relieve mild to moderate pain and reduce high fever quickly.',
      sideEffects: 'Safe at recommended dosage; avoid alcohol overdose.',
      manufacturer: 'Micro Labs Ltd.',
      stocks: { 1: 200, 2: 150, 3: 80 }
    },
    {
      id: 3,
      name: 'Metformin 500mg',
      genericName: 'Metformin Hydrochloride',
      brandName: 'Glucophage / Glycomet',
      category: 'Diabetes Care',
      dosageForm: 'Tablet',
      strength: '500 mg',
      price: 8.75,
      requiresPrescription: true,
      description: 'First-line medication for the treatment of type 2 diabetes, helping control blood sugar levels.',
      sideEffects: 'Mild gastrointestinal discomfort, take with meals.',
      manufacturer: 'USV Pvt Ltd.',
      stocks: { 1: 65, 2: 0, 3: 30 }
    },
    {
      id: 4,
      name: 'Atorvastatin 20mg',
      genericName: 'Atorvastatin Calcium',
      brandName: 'Lipitor / Storvas',
      category: 'Cardiovascular',
      dosageForm: 'Tablet',
      strength: '20 mg',
      price: 15.00,
      requiresPrescription: true,
      description: 'Statin medication used to prevent cardiovascular disease and treat abnormal lipid / cholesterol levels.',
      sideEffects: 'Joint pain, mild headache.',
      manufacturer: 'Sun Pharma Ltd.',
      stocks: { 1: 30, 2: 50, 3: 12 }
    },
    {
      id: 5,
      name: 'Cetirizine 10mg',
      genericName: 'Cetirizine Dihydrochloride',
      brandName: 'Zyrtec / Cetzine',
      category: 'Allergy & Cold',
      dosageForm: 'Tablet',
      strength: '10 mg',
      price: 4.50,
      requiresPrescription: false,
      description: 'Second-generation antihistamine used to relieve allergy symptoms such as watery eyes, runny nose, and sneezing.',
      sideEffects: 'Mild drowsiness in rare cases.',
      manufacturer: 'Dr. Reddy\'s Laboratories',
      stocks: { 1: 120, 2: 90, 3: 45 }
    },
    {
      id: 6,
      name: 'Azithromycin 500mg',
      genericName: 'Azithromycin Monohydrate',
      brandName: 'Zithromax / Azithral',
      category: 'Antibiotics',
      dosageForm: 'Tablet',
      strength: '500 mg',
      price: 18.00,
      requiresPrescription: true,
      description: 'Macrolide antibiotic used for respiratory tract infections, pneumonia, and strep throat infections.',
      sideEffects: 'Diarrhea, stomach pain.',
      manufacturer: 'Alembic Pharmaceuticals',
      stocks: { 1: 0, 2: 24, 3: 15 }
    },
    {
      id: 7,
      name: 'Vitamin D3 60,000 IU',
      genericName: 'Cholecalciferol',
      brandName: 'Calcirol / Uprise D3',
      category: 'Vitamins & Supplements',
      dosageForm: 'Softgel Capsule',
      strength: '60,000 IU',
      price: 9.50,
      requiresPrescription: false,
      description: 'High-potency Vitamin D3 supplement for bone strength, calcium absorption, and immune support.',
      sideEffects: 'None reported when taken weekly.',
      manufacturer: 'Cadila Healthcare',
      stocks: { 1: 150, 2: 110, 3: 95 }
    },
    {
      id: 8,
      name: 'Pantoprazole 40mg',
      genericName: 'Pantoprazole Sodium',
      brandName: 'Pantocid / Pantop',
      category: 'Gastrointestinal',
      dosageForm: 'Tablet',
      strength: '40 mg',
      price: 7.20,
      requiresPrescription: true,
      description: 'Proton pump inhibitor (PPI) that decreases stomach acid production for acidity, GERD, and ulcers.',
      sideEffects: 'Headache, dry mouth.',
      manufacturer: 'Sun Pharma Ltd.',
      stocks: { 1: 85, 2: 60, 3: 40 }
    },
    {
      id: 9,
      name: 'Salbutamol Inhaler 100mcg',
      genericName: 'Albuterol / Salbutamol',
      brandName: 'Ventolin / Asthalin',
      category: 'Respiratory',
      dosageForm: 'Inhaler',
      strength: '100 mcg/dose',
      price: 14.80,
      requiresPrescription: true,
      description: 'Fast-acting bronchodilator for rapid relief of bronchospasm in asthma and COPD attacks.',
      sideEffects: 'Mild shakiness, increased heart rate.',
      manufacturer: 'Cipla Ltd.',
      stocks: { 1: 40, 2: 20, 3: 0 }
    },
    {
      id: 10,
      name: 'Ibuprofen 400mg',
      genericName: 'Ibuprofen',
      brandName: 'Brufen / Advil',
      category: 'Pain Relief & Fever',
      dosageForm: 'Tablet',
      strength: '400 mg',
      price: 5.10,
      requiresPrescription: false,
      description: 'Nonsteroidal anti-inflammatory drug (NSAID) for inflammation, headaches, dental pain, and muscular stiffness.',
      sideEffects: 'Take with food to prevent gastric irritation.',
      manufacturer: 'Abbott Healthcare',
      stocks: { 1: 180, 2: 75, 3: 130 }
    }
  ];

  const INITIAL_ORDERS = [
    {
      id: 'ORD-9081',
      userId: 4,
      userName: 'John Doe',
      pharmacyId: 1,
      pharmacyName: 'Apollo HealthCare & Pharmacy',
      items: [
        { medicineId: 2, name: 'Paracetamol 650mg', qty: 2, price: 3.20 },
        { medicineId: 7, name: 'Vitamin D3 60,000 IU', qty: 1, price: 9.50 }
      ],
      total: 15.90,
      status: 'OUT_FOR_DELIVERY',
      statusStep: 4, // 1: Placed, 2: Verified, 3: Packed, 4: Out for Delivery, 5: Delivered
      type: 'DELIVERY',
      address: '742 Evergreen Terrace, Metro City',
      createdAt: '2026-09-11 19:30',
      hasPrescription: false
    },
    {
      id: 'ORD-9075',
      userId: 4,
      userName: 'John Doe',
      pharmacyId: 2,
      pharmacyName: 'MedPlus 24x7 Chemist',
      items: [
        { medicineId: 1, name: 'Amoxicillin 500mg', qty: 1, price: 12.50 }
      ],
      total: 12.50,
      status: 'VERIFIED',
      statusStep: 2,
      type: 'PICKUP',
      address: 'Store Pickup',
      createdAt: '2026-09-11 16:15',
      hasPrescription: true,
      prescriptionFile: 'Dr_Smith_Amoxil_Rx.pdf'
    },
    {
      id: 'ORD-9060',
      userId: 5,
      userName: 'Sarah Jenkins',
      pharmacyId: 1,
      pharmacyName: 'Apollo HealthCare & Pharmacy',
      items: [
        { medicineId: 4, name: 'Atorvastatin 20mg', qty: 1, price: 15.00 },
        { medicineId: 3, name: 'Metformin 500mg', qty: 1, price: 8.75 }
      ],
      total: 23.75,
      status: 'DELIVERED',
      statusStep: 5,
      type: 'DELIVERY',
      address: '108 Palm Avenue, Green Valley',
      createdAt: '2026-09-10 11:20',
      hasPrescription: true,
      prescriptionFile: 'Lipitor_Glycomet_Rx.pdf'
    }
  ];

  const INITIAL_REQUESTS = [
    {
      id: 'REQ-101',
      userId: 4,
      userName: 'John Doe',
      medicineName: 'Azithromycin 500mg',
      quantity: 2,
      notes: 'Need urgently for chest congestion. Preferred pharmacy in 5km.',
      status: 'RESOLVED',
      pharmacyOffer: 'Apollo Pharmacy has restocked this item.',
      createdAt: '2026-09-10 14:00'
    },
    {
      id: 'REQ-102',
      userId: 5,
      userName: 'Sarah Jenkins',
      medicineName: 'Salbutamol Inhaler 100mcg',
      quantity: 1,
      notes: 'Asthma inhaler backup cartridge needed.',
      status: 'OPEN',
      pharmacyOffer: null,
      createdAt: '2026-09-11 18:45'
    }
  ];

  // ==========================================
  // 2. DATA STORE HELPER (LOCALSTORAGE)
  // ==========================================
  const STORE_KEYS = {
    USERS: 'medifind_users',
    CURRENT_USER: 'medifind_current_user',
    PHARMACIES: 'medifind_pharmacies',
    MEDICINES: 'medifind_medicines',
    ORDERS: 'medifind_orders',
    REQUESTS: 'medifind_requests',
    CART: 'medifind_cart'
  };

  function getFromStore(key, defaultValue) {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : defaultValue;
    } catch (e) {
      console.warn('LocalStorage error:', e);
      return defaultValue;
    }
  }

  function saveToStore(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      console.warn('LocalStorage save error:', e);
    }
  }

  // Seed storage if empty
  function initDataStore() {
    if (!localStorage.getItem(STORE_KEYS.USERS)) {
      saveToStore(STORE_KEYS.USERS, INITIAL_USERS);
    }
    if (!localStorage.getItem(STORE_KEYS.PHARMACIES)) {
      saveToStore(STORE_KEYS.PHARMACIES, INITIAL_PHARMACIES);
    }
    if (!localStorage.getItem(STORE_KEYS.MEDICINES)) {
      saveToStore(STORE_KEYS.MEDICINES, INITIAL_MEDICINES);
    }
    if (!localStorage.getItem(STORE_KEYS.ORDERS)) {
      saveToStore(STORE_KEYS.ORDERS, INITIAL_ORDERS);
    }
    if (!localStorage.getItem(STORE_KEYS.REQUESTS)) {
      saveToStore(STORE_KEYS.REQUESTS, INITIAL_REQUESTS);
    }
    if (!localStorage.getItem(STORE_KEYS.CART)) {
      saveToStore(STORE_KEYS.CART, []);
    }
  }

  initDataStore();

  // ==========================================
  // 3. CORE AUTH ENGINE
  // ==========================================
  const MediAuth = {
    getCurrentUser() {
      return getFromStore(STORE_KEYS.CURRENT_USER, null);
    },

    login(email, password) {
      const users = getFromStore(STORE_KEYS.USERS, INITIAL_USERS);
      const user = users.find(u => u.email.toLowerCase() === email.trim().toLowerCase());

      if (!user) {
        return { success: false, message: 'No account found with this email address.' };
      }

      if (user.password !== password) {
        return { success: false, message: 'Invalid password. Please try again.' };
      }

      saveToStore(STORE_KEYS.CURRENT_USER, user);
      MediUI.triggerAuthUpdate();
      return { success: true, user };
    },

    loginAs(role) {
      const users = getFromStore(STORE_KEYS.USERS, INITIAL_USERS);
      let targetUser = null;
      if (role === 'admin') targetUser = users.find(u => u.role === 'admin');
      else if (role === 'pharmacy') targetUser = users.find(u => u.role === 'pharmacy');
      else targetUser = users.find(u => u.role === 'customer');

      if (targetUser) {
        saveToStore(STORE_KEYS.CURRENT_USER, targetUser);
        MediUI.triggerAuthUpdate();
        return { success: true, user: targetUser };
      }
      return { success: false, message: 'Demo account not found.' };
    },

    registerCustomer(data) {
      const users = getFromStore(STORE_KEYS.USERS, INITIAL_USERS);
      if (users.some(u => u.email.toLowerCase() === data.email.trim().toLowerCase())) {
        return { success: false, message: 'An account with this email already exists.' };
      }

      const newUser = {
        id: Date.now(),
        email: data.email.trim(),
        password: data.password,
        name: data.name,
        phone: data.phone || '+1-555-0000',
        address: data.address || '',
        role: 'customer',
        avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop&q=80'
      };

      users.push(newUser);
      saveToStore(STORE_KEYS.USERS, users);
      saveToStore(STORE_KEYS.CURRENT_USER, newUser);
      MediUI.triggerAuthUpdate();
      return { success: true, user: newUser };
    },

    registerPharmacy(data) {
      const users = getFromStore(STORE_KEYS.USERS, INITIAL_USERS);
      const pharmacies = getFromStore(STORE_KEYS.PHARMACIES, INITIAL_PHARMACIES);

      if (users.some(u => u.email.toLowerCase() === data.email.trim().toLowerCase())) {
        return { success: false, message: 'An account with this email already exists.' };
      }

      const newPharmacyId = pharmacies.length + 1;
      const newPharmacy = {
        id: newPharmacyId,
        name: data.pharmacyName,
        licenseNumber: data.licenseNumber,
        phone: data.phone,
        email: data.email,
        address: data.address,
        city: data.city || 'Metro City',
        state: data.state || 'Central',
        pincode: data.pincode || '100001',
        latitude: parseFloat(data.latitude) || 28.6139,
        longitude: parseFloat(data.longitude) || 77.2090,
        rating: 5.0,
        reviewsCount: 1,
        is24x7: !!data.is24x7,
        homeDelivery: !!data.homeDelivery,
        status: 'PENDING',
        openHours: data.openHours || '8:00 AM - 10:00 PM',
        image: 'https://images.unsplash.com/photo-1586015555751-63bb77f4322a?w=400&auto=format&fit=crop&q=80'
      };

      pharmacies.push(newPharmacy);
      saveToStore(STORE_KEYS.PHARMACIES, pharmacies);

      const newUser = {
        id: Date.now(),
        email: data.email.trim(),
        password: data.password,
        name: data.ownerName || data.pharmacyName,
        phone: data.phone,
        role: 'pharmacy',
        pharmacyId: newPharmacyId,
        avatar: 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=100&auto=format&fit=crop&q=80'
      };

      users.push(newUser);
      saveToStore(STORE_KEYS.USERS, users);
      saveToStore(STORE_KEYS.CURRENT_USER, newUser);
      MediUI.triggerAuthUpdate();
      return { success: true, user: newUser, pharmacy: newPharmacy };
    },

    logout() {
      localStorage.removeItem(STORE_KEYS.CURRENT_USER);
      MediUI.triggerAuthUpdate();
      MediUI.showToast('You have been logged out successfully.', 'info');
    }
  };

  // ==========================================
  // 4. CART & ORDER SERVICE
  // ==========================================
  const MediCart = {
    getItems() {
      return getFromStore(STORE_KEYS.CART, []);
    },

    addItem(medicineId, pharmacyId, qty = 1) {
      const medicines = getFromStore(STORE_KEYS.MEDICINES, INITIAL_MEDICINES);
      const pharmacies = getFromStore(STORE_KEYS.PHARMACIES, INITIAL_PHARMACIES);
      const medicine = medicines.find(m => m.id === medicineId);
      const pharmacy = pharmacies.find(p => p.id === pharmacyId);

      if (!medicine || !pharmacy) return false;

      const cart = this.getItems();
      const existing = cart.find(i => i.medicineId === medicineId && i.pharmacyId === pharmacyId);

      if (existing) {
        existing.qty += qty;
      } else {
        cart.push({
          medicineId: medicine.id,
          name: medicine.name,
          genericName: medicine.genericName,
          strength: medicine.strength,
          price: medicine.price,
          requiresPrescription: medicine.requiresPrescription,
          pharmacyId: pharmacy.id,
          pharmacyName: pharmacy.name,
          qty: qty
        });
      }

      saveToStore(STORE_KEYS.CART, cart);
      MediUI.updateCartBadge();
      MediUI.showToast(`Added "${medicine.name}" to cart!`, 'success');
      return true;
    },

    updateQty(index, newQty) {
      const cart = this.getItems();
      if (newQty <= 0) {
        cart.splice(index, 1);
      } else {
        cart[index].qty = newQty;
      }
      saveToStore(STORE_KEYS.CART, cart);
      MediUI.updateCartBadge();
    },

    clear() {
      saveToStore(STORE_KEYS.CART, []);
      MediUI.updateCartBadge();
    },

    getTotal() {
      return this.getItems().reduce((sum, item) => sum + (item.price * item.qty), 0);
    },

    checkout(orderData) {
      const user = MediAuth.getCurrentUser();
      if (!user) {
        MediUI.openModal('login-modal');
        MediUI.showToast('Please login to place your order.', 'warning');
        return false;
      }

      const cart = this.getItems();
      if (cart.length === 0) return false;

      const orders = getFromStore(STORE_KEYS.ORDERS, INITIAL_ORDERS);
      const newOrderId = 'ORD-' + Math.floor(1000 + Math.random() * 9000);

      const newOrder = {
        id: newOrderId,
        userId: user.id,
        userName: user.name,
        pharmacyId: cart[0].pharmacyId,
        pharmacyName: cart[0].pharmacyName,
        items: [...cart],
        total: this.getTotal(),
        status: 'PLACED',
        statusStep: 1,
        type: orderData.deliveryType || 'DELIVERY',
        address: orderData.address || user.address || 'Standard Delivery Address',
        createdAt: new Date().toISOString().replace('T', ' ').substring(0, 16),
        hasPrescription: cart.some(i => i.requiresPrescription),
        prescriptionFile: orderData.prescriptionFileName || null
      };

      // Decrement inventory
      const medicines = getFromStore(STORE_KEYS.MEDICINES, INITIAL_MEDICINES);
      cart.forEach(item => {
        const med = medicines.find(m => m.id === item.medicineId);
        if (med && med.stocks && med.stocks[item.pharmacyId] !== undefined) {
          med.stocks[item.pharmacyId] = Math.max(0, med.stocks[item.pharmacyId] - item.qty);
        }
      });
      saveToStore(STORE_KEYS.MEDICINES, medicines);

      orders.unshift(newOrder);
      saveToStore(STORE_KEYS.ORDERS, orders);
      this.clear();

      MediUI.showToast(`Order ${newOrderId} placed successfully!`, 'success');
      return newOrder;
    }
  };

  // ==========================================
  // 5. TOAST & MODAL SYSTEM (UI CONTROLLER)
  // ==========================================
  const MediUI = {
    showToast(message, type = 'info') {
      let container = document.getElementById('toast-container');
      if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
      }

      const icons = {
        success: 'fa-circle-check',
        error: 'fa-circle-exclamation',
        warning: 'fa-triangle-exclamation',
        info: 'fa-circle-info'
      };

      const toast = document.createElement('div');
      toast.className = `toast-card toast-${type}`;
      toast.innerHTML = `
        <i class="fa-solid ${icons[type] || 'fa-circle-info'} toast-icon"></i>
        <div class="toast-content">${message}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
      `;

      container.appendChild(toast);

      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        setTimeout(() => toast.remove(), 300);
      }, 4500);
    },

    openModal(modalId) {
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
      }
    },

    closeModal(modalId) {
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
      }
    },

    closeAllModals() {
      document.querySelectorAll('.medifind-modal.active').forEach(m => m.classList.remove('active'));
      document.body.style.overflow = '';
    },

    updateCartBadge() {
      const cart = MediCart.getItems();
      const count = cart.reduce((sum, i) => sum + i.qty, 0);
      document.querySelectorAll('.cart-badge-count').forEach(el => {
        el.textContent = count;
        el.style.display = count > 0 ? 'inline-flex' : 'none';
      });
    },

    triggerAuthUpdate() {
      const user = MediAuth.getCurrentUser();
      const authSlots = document.querySelectorAll('[data-auth-slot]');

      authSlots.forEach(slot => {
        if (user) {
          let dashboardLink = '#';
          let roleBadge = '';
          if (user.role === 'admin') {
            dashboardLink = 'dashboard_admin.html';
            roleBadge = '<span class="badge badge-danger">Admin</span>';
          } else if (user.role === 'pharmacy') {
            dashboardLink = 'dashboard_pharmacy.html';
            roleBadge = '<span class="badge badge-success">Pharmacy</span>';
          } else {
            dashboardLink = 'dashboard_customer.html';
            roleBadge = '<span class="badge badge-info">Customer</span>';
          }

          slot.innerHTML = `
            <div class="user-menu-wrapper" style="display:inline-flex; align-items:center; gap:0.75rem;">
              <a href="${dashboardLink}" class="btn btn-outline btn-sm user-profile-pill" style="display:inline-flex; align-items:center; gap:0.5rem;">
                <img src="${user.avatar || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100'}" alt="User" style="width:24px; height:24px; border-radius:50%; object-fit:cover;">
                <span>${user.name.split(' ')[0]}</span>
                ${roleBadge}
              </a>
              <button class="btn btn-outline btn-sm" onclick="MediAuth.logout()" title="Logout" style="padding:0.4rem 0.6rem;">
                <i class="fa-solid fa-arrow-right-from-bracket"></i>
              </button>
            </div>
          `;
        } else {
          slot.innerHTML = `
            <button type="button" class="btn btn-outline btn-sm" onclick="MediUI.openModal('login-modal')">Login</button>
            <button type="button" class="btn btn-primary btn-sm" onclick="MediUI.openModal('register-choice-modal')">Register</button>
          `;
        }
      });

      this.updateCartBadge();
    },

    // Inject shared modal markup if not already present on page
    injectCommonModals() {
      if (document.getElementById('login-modal')) return;

      const modalWrapper = document.createElement('div');
      modalWrapper.innerHTML = `
        <!-- 1. LOGIN MODAL -->
        <div id="login-modal" class="medifind-modal">
          <div class="modal-backdrop" onclick="MediUI.closeModal('login-modal')"></div>
          <div class="modal-dialog" style="max-width:420px;">
            <div class="modal-header">
              <h3 style="margin:0; font-size:1.25rem; font-weight:700;">Sign In</h3>
              <button class="modal-close-btn" onclick="MediUI.closeModal('login-modal')">&times;</button>
            </div>
            <div class="modal-body" style="padding:1.5rem;">
              <form id="modal-login-form" onsubmit="MediUI.handleModalLogin(event)">
                <div class="form-group" style="margin-bottom:1.25rem;">
                  <label class="form-label" for="login-email">Email Address</label>
                  <input type="email" id="login-email" class="form-control" placeholder="name@example.com" required autofocus>
                </div>
                <div class="form-group" style="margin-bottom:1.5rem;">
                  <label class="form-label" for="login-password">Password</label>
                  <input type="password" id="login-password" class="form-control" placeholder="Enter your password" required>
                </div>

                <button type="submit" class="btn btn-primary btn-lg" style="width:100%;">
                  Sign In
                </button>
              </form>
            </div>
            <div class="modal-footer" style="text-align:center; font-size:0.88rem; color:var(--text-muted); background:var(--bg-subtle);">
              Don't have an account? 
              <a href="javascript:void(0)" onclick="MediUI.closeModal('login-modal'); MediUI.openModal('register-choice-modal');" style="font-weight:700; color:var(--primary);">
                Register
              </a>
            </div>
          </div>
        </div>

        <!-- 2. REGISTER CHOICE MODAL -->
        <div id="register-choice-modal" class="medifind-modal">
          <div class="modal-backdrop" onclick="MediUI.closeModal('register-choice-modal')"></div>
          <div class="modal-dialog" style="max-width:480px;">
            <div class="modal-header">
              <h3 style="margin:0; font-size:1.25rem; font-weight:700;">Create an Account</h3>
              <button class="modal-close-btn" onclick="MediUI.closeModal('register-choice-modal')">&times;</button>
            </div>
            <div class="modal-body" style="padding:1.5rem;">
              <p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:1.25rem;">
                Select your account type to proceed:
              </p>
              
              <div style="display:flex; flex-direction:column; gap:1rem;">
                <button type="button" class="btn btn-outline" style="padding:1.15rem; text-align:left; display:flex; justify-content:space-between; align-items:center; border:1px solid var(--border-color); border-radius:var(--radius-md);" onclick="MediUI.closeModal('register-choice-modal'); MediUI.openModal('register-customer-modal');">
                  <div>
                    <strong style="display:block; font-size:1.05rem; color:var(--text-main); margin-bottom:0.25rem;"><i class="fa-solid fa-user text-primary" style="margin-right:0.5rem;"></i> Register as Customer</strong>
                    <span style="font-size:0.85rem; color:var(--text-muted);">Search medicines and order from local verified pharmacies</span>
                  </div>
                  <i class="fa-solid fa-chevron-right text-muted"></i>
                </button>

                <button type="button" class="btn btn-outline" style="padding:1.15rem; text-align:left; display:flex; justify-content:space-between; align-items:center; border:1px solid var(--border-color); border-radius:var(--radius-md);" onclick="MediUI.closeModal('register-choice-modal'); MediUI.openModal('register-pharmacy-modal');">
                  <div>
                    <strong style="display:block; font-size:1.05rem; color:var(--text-main); margin-bottom:0.25rem;"><i class="fa-solid fa-store text-accent" style="margin-right:0.5rem;"></i> Register as Pharmacy</strong>
                    <span style="font-size:0.85rem; color:var(--text-muted);">Register your store and manage medicine availability</span>
                  </div>
                  <i class="fa-solid fa-chevron-right text-muted"></i>
                </button>
              </div>
            </div>
            <div class="modal-footer" style="text-align:center; font-size:0.88rem; color:var(--text-muted); background:var(--bg-subtle);">
              Already have an account? 
              <a href="javascript:void(0)" onclick="MediUI.closeModal('register-choice-modal'); MediUI.openModal('login-modal');" style="font-weight:700; color:var(--primary);">
                Sign In
              </a>
            </div>
          </div>
        </div>

        <!-- 3. CUSTOMER REGISTRATION MODAL -->
        <div id="register-customer-modal" class="medifind-modal">
          <div class="modal-backdrop" onclick="MediUI.closeModal('register-customer-modal')"></div>
          <div class="modal-dialog">
            <div class="modal-header">
              <div style="display:flex; align-items:center; gap:0.6rem;">
                <div class="brand-icon" style="width:32px; height:32px; font-size:0.9rem;"><i class="fa-solid fa-user-plus"></i></div>
                <h3 style="margin:0; font-size:1.3rem;">Register as Customer</h3>
              </div>
              <button class="modal-close-btn" onclick="MediUI.closeModal('register-customer-modal')">&times;</button>
            </div>
            <div class="modal-body">
              <form id="customer-register-form" onsubmit="MediUI.handleCustomerRegister(event)">
                <div class="form-group" style="margin-bottom:0.85rem;">
                  <label class="form-label" for="reg-cust-name">Full Name</label>
                  <input type="text" id="reg-cust-name" class="form-control" placeholder="e.g. John Doe" required>
                </div>
                <div class="form-group" style="margin-bottom:0.85rem;">
                  <label class="form-label" for="reg-cust-email">Email Address</label>
                  <input type="email" id="reg-cust-email" class="form-control" placeholder="e.g. john@example.com" required>
                </div>
                <div class="form-group" style="margin-bottom:0.85rem;">
                  <label class="form-label" for="reg-cust-phone">Phone Number</label>
                  <input type="tel" id="reg-cust-phone" class="form-control" placeholder="+1-555-0100" required>
                </div>
                <div class="form-group" style="margin-bottom:0.85rem;">
                  <label class="form-label" for="reg-cust-address">Delivery Address</label>
                  <input type="text" id="reg-cust-address" class="form-control" placeholder="Street Address, City, Zipcode" required>
                </div>
                <div class="form-group" style="margin-bottom:1.25rem;">
                  <label class="form-label" for="reg-cust-password">Create Password</label>
                  <input type="password" id="reg-cust-password" class="form-control" placeholder="At least 6 characters" minlength="6" required>
                </div>
                <button type="submit" class="btn btn-primary btn-lg" style="width:100%;">
                  <i class="fa-solid fa-check"></i> Complete Customer Registration
                </button>
              </form>
            </div>
          </div>
        </div>

        <!-- 4. PHARMACY REGISTRATION MODAL -->
        <div id="register-pharmacy-modal" class="medifind-modal">
          <div class="modal-backdrop" onclick="MediUI.closeModal('register-pharmacy-modal')"></div>
          <div class="modal-dialog" style="max-width:540px;">
            <div class="modal-header">
              <div style="display:flex; align-items:center; gap:0.6rem;">
                <div class="brand-icon" style="width:32px; height:32px; font-size:0.9rem; background:linear-gradient(135deg, #059669, #047857);"><i class="fa-solid fa-prescription-bottle-medical"></i></div>
                <h3 style="margin:0; font-size:1.3rem;">Register Pharmacy Store</h3>
              </div>
              <button class="modal-close-btn" onclick="MediUI.closeModal('register-pharmacy-modal')">&times;</button>
            </div>
            <div class="modal-body">
              <form id="pharmacy-register-form" onsubmit="MediUI.handlePharmacyRegister(event)">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin-bottom:0.75rem;">
                  <div class="form-group">
                    <label class="form-label" for="reg-pharm-name">Pharmacy Name</label>
                    <input type="text" id="reg-pharm-name" class="form-control" placeholder="e.g. Care Point Chemist" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label" for="reg-pharm-owner">Pharmacist / Owner Name</label>
                    <input type="text" id="reg-pharm-owner" class="form-control" placeholder="e.g. Dr. Jane Smith" required>
                  </div>
                </div>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin-bottom:0.75rem;">
                  <div class="form-group">
                    <label class="form-label" for="reg-pharm-license">Drug License No.</label>
                    <input type="text" id="reg-pharm-license" class="form-control" placeholder="e.g. DL-2026-MED-9912" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label" for="reg-pharm-phone">Store Contact Phone</label>
                    <input type="tel" id="reg-pharm-phone" class="form-control" placeholder="+1-555-0199" required>
                  </div>
                </div>

                <div class="form-group" style="margin-bottom:0.75rem;">
                  <label class="form-label" for="reg-pharm-email">Official Store Email</label>
                  <input type="email" id="reg-pharm-email" class="form-control" placeholder="contact@carepoint.example.com" required>
                </div>

                <div class="form-group" style="margin-bottom:0.75rem;">
                  <label class="form-label" for="reg-pharm-address">Physical Store Address</label>
                  <input type="text" id="reg-pharm-address" class="form-control" placeholder="Full street address & landmark" required>
                </div>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin-bottom:0.75rem;">
                  <div class="form-group">
                    <label class="form-label" for="reg-pharm-hours">Operating Hours</label>
                    <input type="text" id="reg-pharm-hours" class="form-control" value="8:00 AM - 10:00 PM">
                  </div>
                  <div class="form-group">
                    <label class="form-label" for="reg-pharm-pass">Password</label>
                    <input type="password" id="reg-pharm-pass" class="form-control" placeholder="••••••••" minlength="6" required>
                  </div>
                </div>

                <div style="display:flex; gap:1.5rem; margin-bottom:1.25rem;">
                  <label style="display:flex; align-items:center; gap:0.4rem; font-size:0.85rem; cursor:pointer;">
                    <input type="checkbox" id="reg-pharm-24x7"> 24x7 Pharmacy
                  </label>
                  <label style="display:flex; align-items:center; gap:0.4rem; font-size:0.85rem; cursor:pointer;">
                    <input type="checkbox" id="reg-pharm-delivery" checked> Supports Home Delivery
                  </label>
                </div>

                <button type="submit" class="btn btn-primary btn-lg" style="width:100%; background:linear-gradient(135deg, #059669 0%, #047857 100%);">
                  <i class="fa-solid fa-hospital"></i> Register & Submit Pharmacy Application
                </button>
              </form>
            </div>
          </div>
        </div>

        <!-- 5. CART & CHECKOUT MODAL -->
        <div id="cart-modal" class="medifind-modal">
          <div class="modal-backdrop" onclick="MediUI.closeModal('cart-modal')"></div>
          <div class="modal-dialog" style="max-width:560px;">
            <div class="modal-header">
              <div style="display:flex; align-items:center; gap:0.6rem;">
                <div class="brand-icon" style="width:32px; height:32px; font-size:0.9rem;"><i class="fa-solid fa-cart-shopping"></i></div>
                <h3 style="margin:0; font-size:1.3rem;">Your Medicine Cart</h3>
              </div>
              <button class="modal-close-btn" onclick="MediUI.closeModal('cart-modal')">&times;</button>
            </div>
            <div class="modal-body" id="cart-modal-content">
              <!-- Dynamically populated -->
            </div>
          </div>
        </div>

        <!-- 6. REQUEST MEDICINE MODAL -->
        <div id="request-modal" class="medifind-modal">
          <div class="modal-backdrop" onclick="MediUI.closeModal('request-modal')"></div>
          <div class="modal-dialog">
            <div class="modal-header">
              <div style="display:flex; align-items:center; gap:0.6rem;">
                <div class="brand-icon" style="width:32px; height:32px; font-size:0.9rem; background:linear-gradient(135deg, #f59e0b, #d97706);"><i class="fa-solid fa-bullhorn"></i></div>
                <h3 style="margin:0; font-size:1.3rem;">Request Out-of-Stock Medicine</h3>
              </div>
              <button class="modal-close-btn" onclick="MediUI.closeModal('request-modal')">&times;</button>
            </div>
            <div class="modal-body">
              <p style="color:var(--text-muted); font-size:0.88rem; margin-bottom:1rem;">
                Can't find your prescription medicine nearby? Post a request and all verified pharmacies in your radius will be alerted to source and stock it for you.
              </p>
              <form id="medicine-request-form" onsubmit="MediUI.handleMedicineRequest(event)">
                <div class="form-group" style="margin-bottom:0.85rem;">
                  <label class="form-label" for="req-med-name">Medicine Name & Strength</label>
                  <input type="text" id="req-med-name" class="form-control" placeholder="e.g. Azithromycin 500mg" required>
                </div>
                <div class="form-group" style="margin-bottom:0.85rem;">
                  <label class="form-label" for="req-med-qty">Quantity Needed</label>
                  <input type="number" id="req-med-qty" class="form-control" value="1" min="1" max="100" required>
                </div>
                <div class="form-group" style="margin-bottom:1.25rem;">
                  <label class="form-label" for="req-med-notes">Urgency / Additional Notes</label>
                  <textarea id="req-med-notes" class="form-control" rows="3" placeholder="e.g. Need within 24 hours, doctor prescribed for acute allergy."></textarea>
                </div>
                <button type="submit" class="btn btn-primary btn-lg" style="width:100%; background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                  <i class="fa-solid fa-paper-plane"></i> Broadcast Request to Local Pharmacies
                </button>
              </form>
            </div>
          </div>
        </div>
      `;
      document.body.appendChild(modalWrapper);
    },

    demoLogin(role) {
      const res = MediAuth.loginAs(role);
      if (res.success) {
        this.closeAllModals();
        this.showToast(`Logged in successfully as ${res.user.name} (${res.user.role.toUpperCase()})!`, 'success');
        
        // If on a specific page or dashboard, reload to reflect data
        if (window.location.pathname.includes('dashboard') || window.location.pathname.includes('login') || window.location.pathname.includes('register')) {
          if (res.user.role === 'admin') window.location.href = 'dashboard_admin.html';
          else if (res.user.role === 'pharmacy') window.location.href = 'dashboard_pharmacy.html';
          else window.location.href = 'dashboard_customer.html';
        }
      } else {
        this.showToast(res.message, 'error');
      }
    },

    handleModalLogin(e) {
      e.preventDefault();
      const email = document.getElementById('login-email').value;
      const pass = document.getElementById('login-password').value;

      const res = MediAuth.login(email, pass);
      if (res.success) {
        this.closeAllModals();
        this.showToast(`Welcome back, ${res.user.name}!`, 'success');
        if (res.user.role === 'admin') window.location.href = 'dashboard_admin.html';
        else if (res.user.role === 'pharmacy') window.location.href = 'dashboard_pharmacy.html';
        else if (window.location.pathname.includes('login') || window.location.pathname.includes('register')) {
          window.location.href = 'index.html';
        }
      } else {
        this.showToast(res.message, 'error');
      }
    },

    handleCustomerRegister(e) {
      e.preventDefault();
      const name = document.getElementById('reg-cust-name').value;
      const email = document.getElementById('reg-cust-email').value;
      const phone = document.getElementById('reg-cust-phone').value;
      const address = document.getElementById('reg-cust-address').value;
      const password = document.getElementById('reg-cust-password').value;

      const res = MediAuth.registerCustomer({ name, email, phone, address, password });
      if (res.success) {
        this.closeAllModals();
        this.showToast(`Account created! Welcome to MediFind, ${res.user.name}!`, 'success');
      } else {
        this.showToast(res.message, 'error');
      }
    },

    handlePharmacyRegister(e) {
      e.preventDefault();
      const pharmacyName = document.getElementById('reg-pharm-name').value;
      const ownerName = document.getElementById('reg-pharm-owner').value;
      const licenseNumber = document.getElementById('reg-pharm-license').value;
      const phone = document.getElementById('reg-pharm-phone').value;
      const email = document.getElementById('reg-pharm-email').value;
      const address = document.getElementById('reg-pharm-address').value;
      const openHours = document.getElementById('reg-pharm-hours').value;
      const password = document.getElementById('reg-pharm-pass').value;
      const is24x7 = document.getElementById('reg-pharm-24x7').checked;
      const homeDelivery = document.getElementById('reg-pharm-delivery').checked;

      const res = MediAuth.registerPharmacy({
        pharmacyName, ownerName, licenseNumber, phone, email, address, openHours, password, is24x7, homeDelivery
      });

      if (res.success) {
        this.closeAllModals();
        this.showToast(`Pharmacy "${res.pharmacy.name}" registered successfully!`, 'success');
        setTimeout(() => {
          window.location.href = 'dashboard_pharmacy.html';
        }, 1000);
      } else {
        this.showToast(res.message, 'error');
      }
    },

    handleMedicineRequest(e) {
      e.preventDefault();
      const user = MediAuth.getCurrentUser();
      if (!user) {
        this.openModal('login-modal');
        this.showToast('Please login first to submit a medicine request.', 'warning');
        return;
      }

      const medicineName = document.getElementById('req-med-name').value;
      const quantity = parseInt(document.getElementById('req-med-qty').value, 10) || 1;
      const notes = document.getElementById('req-med-notes').value;

      const requests = getFromStore(STORE_KEYS.REQUESTS, INITIAL_REQUESTS);
      const newReq = {
        id: 'REQ-' + Math.floor(100 + Math.random() * 900),
        userId: user.id,
        userName: user.name,
        medicineName,
        quantity,
        notes,
        status: 'OPEN',
        pharmacyOffer: null,
        createdAt: new Date().toISOString().replace('T', ' ').substring(0, 16)
      };

      requests.unshift(newReq);
      saveToStore(STORE_KEYS.REQUESTS, requests);

      this.closeModal('request-modal');
      this.showToast(`Medicine request for "${medicineName}" sent to local pharmacies!`, 'success');
      document.getElementById('medicine-request-form').reset();
    },

    renderCartModal() {
      const container = document.getElementById('cart-modal-content');
      if (!container) return;

      const cart = MediCart.getItems();
      const user = MediAuth.getCurrentUser();

      if (cart.length === 0) {
        container.innerHTML = `
          <div style="text-align:center; padding:2.5rem 1rem;">
            <div style="font-size:3rem; color:var(--text-subtle); margin-bottom:1rem;"><i class="fa-solid fa-basket-shopping"></i></div>
            <h4 style="margin-bottom:0.5rem;">Your Cart is Empty</h4>
            <p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:1.5rem;">Search medicines and add them to your cart from verified pharmacies.</p>
            <a href="search.html" class="btn btn-primary" onclick="MediUI.closeModal('cart-modal')">Browse Medicines</a>
          </div>
        `;
        return;
      }

      const hasRx = cart.some(i => i.requiresPrescription);
      const total = MediCart.getTotal();

      let itemsHtml = cart.map((item, idx) => `
        <div class="cart-item-row">
          <div style="flex:1;">
            <div style="font-weight:700; font-size:0.95rem; color:var(--text-main);">${item.name}</div>
            <div style="font-size:0.8rem; color:var(--text-muted);">
              <i class="fa-solid fa-shop"></i> ${item.pharmacyName}
              ${item.requiresPrescription ? '<span class="badge badge-warning" style="font-size:0.65rem; margin-left:0.3rem;"><i class="fa-solid fa-prescription"></i> Rx Required</span>' : ''}
            </div>
            <div style="font-size:0.88rem; font-weight:700; color:var(--primary); margin-top:0.2rem;">₹${(item.price * item.qty).toFixed(2)} (₹${item.price.toFixed(2)} each)</div>
          </div>
          <div style="display:flex; align-items:center; gap:0.5rem;">
            <button class="qty-btn" onclick="MediCart.updateQty(${idx}, ${item.qty - 1}); MediUI.renderCartModal();">-</button>
            <span style="font-weight:700; width:20px; text-align:center;">${item.qty}</span>
            <button class="qty-btn" onclick="MediCart.updateQty(${idx}, ${item.qty + 1}); MediUI.renderCartModal();">+</button>
            <button class="btn-delete-item" onclick="MediCart.updateQty(${idx}, 0); MediUI.renderCartModal();" title="Remove"><i class="fa-solid fa-trash-can"></i></button>
          </div>
        </div>
      `).join('');

      container.innerHTML = `
        <div class="cart-items-list" style="max-height:260px; overflow-y:auto; margin-bottom:1rem; border-bottom:1px solid var(--border-color); padding-bottom:1rem;">
          ${itemsHtml}
        </div>

        ${hasRx ? `
          <div class="prescription-alert-box">
            <i class="fa-solid fa-triangle-exclamation" style="color:#d97706; font-size:1.2rem;"></i>
            <div style="font-size:0.82rem; color:#92400e;">
              <strong>Prescription Item Detected:</strong> One or more items in your cart require a valid medical prescription for fulfillment.
              <div style="margin-top:0.5rem;">
                <input type="file" id="order-prescription-file" class="form-control" style="font-size:0.8rem; padding:0.3rem 0.6rem;">
              </div>
            </div>
          </div>
        ` : ''}

        <div style="margin-bottom:1rem;">
          <label class="form-label" style="font-size:0.85rem;">Delivery Method</label>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem;">
            <label class="delivery-option active">
              <input type="radio" name="delivery-mode" value="DELIVERY" checked>
              <span><i class="fa-solid fa-truck"></i> Home Delivery</span>
            </label>
            <label class="delivery-option">
              <input type="radio" name="delivery-mode" value="PICKUP">
              <span><i class="fa-solid fa-store"></i> Store Pickup</span>
            </label>
          </div>
        </div>

        <div class="form-group" style="margin-bottom:1rem;">
          <label class="form-label" style="font-size:0.85rem;">Delivery Address</label>
          <input type="text" id="order-address-input" class="form-control" value="${user ? (user.address || '') : ''}" placeholder="Enter full delivery address" required>
        </div>

        <div class="cart-summary-box">
          <div style="display:flex; justify-content:space-between; margin-bottom:0.35rem; font-size:0.88rem; color:var(--text-muted);">
            <span>Subtotal</span>
            <span>₹${total.toFixed(2)}</span>
          </div>
          <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem; font-size:0.88rem; color:var(--text-muted);">
            <span>Estimated Delivery Fee</span>
            <span style="color:var(--accent); font-weight:600;">FREE</span>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:1.15rem; font-weight:800; color:var(--text-main); border-top:1px solid var(--border-color); padding-top:0.5rem;">
            <span>Total Payable</span>
            <span style="color:var(--primary);">₹${total.toFixed(2)}</span>
          </div>
        </div>

        <button type="button" class="btn btn-primary btn-lg" style="width:100%; margin-top:1rem;" onclick="MediUI.handleCartCheckout()">
          <i class="fa-solid fa-shield-check"></i> Place Order Now (₹${total.toFixed(2)})
        </button>
      `;
    },

    handleCartCheckout() {
      const address = document.getElementById('order-address-input') ? document.getElementById('order-address-input').value : '';
      const deliveryModeEl = document.querySelector('input[name="delivery-mode"]:checked');
      const deliveryType = deliveryModeEl ? deliveryModeEl.value : 'DELIVERY';
      const fileInput = document.getElementById('order-prescription-file');
      const prescriptionFileName = fileInput && fileInput.files[0] ? fileInput.files[0].name : 'Uploaded_Prescription.pdf';

      const order = MediCart.checkout({
        address,
        deliveryType,
        prescriptionFileName
      });

      if (order) {
        this.closeModal('cart-modal');
        setTimeout(() => {
          window.location.href = 'dashboard_customer.html';
        }, 1200);
      }
    }
  };

  // ==========================================
  // 6. INITIALIZATION & GLOBAL EXPORT
  // ==========================================
  window.MediAuth = MediAuth;
  window.MediCart = MediCart;
  window.MediUI = MediUI;
  window.MediStore = {
    getUsers: () => getFromStore(STORE_KEYS.USERS, INITIAL_USERS),
    getPharmacies: () => getFromStore(STORE_KEYS.PHARMACIES, INITIAL_PHARMACIES),
    getMedicines: () => getFromStore(STORE_KEYS.MEDICINES, INITIAL_MEDICINES),
    getOrders: () => getFromStore(STORE_KEYS.ORDERS, INITIAL_ORDERS),
    getRequests: () => getFromStore(STORE_KEYS.REQUESTS, INITIAL_REQUESTS),
    saveUsers: (data) => saveToStore(STORE_KEYS.USERS, data),
    savePharmacies: (data) => saveToStore(STORE_KEYS.PHARMACIES, data),
    saveMedicines: (data) => saveToStore(STORE_KEYS.MEDICINES, data),
    saveOrders: (data) => saveToStore(STORE_KEYS.ORDERS, data),
    saveRequests: (data) => saveToStore(STORE_KEYS.REQUESTS, data)
  };

  document.addEventListener('DOMContentLoaded', () => {
    MediUI.injectCommonModals();
    MediUI.triggerAuthUpdate();
    MediUI.updateCartBadge();

    // Hook cart trigger buttons
    document.querySelectorAll('[data-action="open-cart"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        MediUI.renderCartModal();
        MediUI.openModal('cart-modal');
      });
    });

    // Hook request medicine buttons
    document.querySelectorAll('[data-action="open-request"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        MediUI.openModal('request-modal');
      });
    });
  });

})();
