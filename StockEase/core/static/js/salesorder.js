// salesorder.js
// Dynamic logic for SalesOrder form: add/remove rows, warehouse filtering, totals, AJAX submit

document.addEventListener('DOMContentLoaded', function () {
  const products = JSON.parse(document.getElementById('productsJson').textContent);
  const warehouses = JSON.parse(document.getElementById('warehousesJson').textContent);
  const inventory = JSON.parse(document.getElementById('inventoryJson').textContent);

  const itemsBody = document.getElementById('items-body');
  const addBtn = document.getElementById('add-item');
  const form = document.getElementById('salesorder-form');

  function getProductById(id) {
    return products.find(p => p.id == id);
  }
  function getWarehouseById(id) {
    return warehouses.find(w => w.id == id);
  }
  function getAvailableWarehouses(productId, quantity) {
    // Return warehouses with enough stock for this product
    return inventory
      .filter(inv => inv.product_id == productId && inv.quantityAvailable >= (quantity || 1))
      .map(inv => getWarehouseById(inv.warehouse_id))
      .filter(Boolean);
  }
  function getAvailableQty(productId, warehouseId) {
    const inv = inventory.find(inv => inv.product_id == productId && inv.warehouse_id == warehouseId);
    return inv ? inv.quantityAvailable : 0;
  }

  function recalcRow(row) {
    const productId = row.querySelector('.product').value;
    const qty = parseInt(row.querySelector('.quantity').value) || 0;
    const product = getProductById(productId);
    row.querySelector('.totalAmount').value = product ? (product.sellingPrice * qty).toFixed(2) : '0.00';
  }

  function recalcAllTotals() {
    let total = 0;
    itemsBody.querySelectorAll('.item-row').forEach(row => {
      recalcRow(row);
      total += parseFloat(row.querySelector('.totalAmount').value) || 0;
    });
    // Optionally show total somewhere
  }

  function updateWarehouseOptions(row) {
    const productId = row.querySelector('.product').value;
    const qty = parseInt(row.querySelector('.quantity').value) || 1;
    const warehouseSelect = row.querySelector('.warehouse');
    const selected = warehouseSelect.value;
    warehouseSelect.innerHTML = '<option value="">Select warehouse</option>';
    if (!productId) return;
    const available = getAvailableWarehouses(productId, qty);
    available.forEach(w => {
      const opt = document.createElement('option');
      opt.value = w.id;
      opt.textContent = w.name;
      if (w.id == selected) opt.selected = true;
      warehouseSelect.appendChild(opt);
    });
    // If selected warehouse is no longer valid, clear selection
    if (!available.some(w => w.id == selected)) warehouseSelect.value = '';
  }

  function addRow(productId = '', warehouseId = '', qty = '', totalAmount = '') {
    const tr = document.createElement('tr');
    tr.className = 'item-row hover:bg-gray-50 transition-colors duration-150';
    tr.innerHTML = `
      <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-500">
        <select class="product input input-sm input-bordered w-full focus:ring-indigo-500 focus:border-indigo-500 border-gray-300 rounded-md" required>
          <option value="">Select product</option>
          ${products.map(p => `<option value="${p.id}" ${p.id == productId ? 'selected' : ''}>${p.name}</option>`).join('')}
        </select>
      </td>
      <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-500">
        <select class="warehouse input input-sm input-bordered w-full focus:ring-indigo-500 focus:border-indigo-500 border-gray-300 rounded-md" required></select>
      </td>
      <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-500"><input type="number" class="quantity input input-sm input-bordered w-full focus:ring-indigo-500 focus:border-indigo-500 border-gray-300 rounded-md" min="1" value="${qty || 1}" required></td>
      <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-500"><input type="text" class="totalAmount input input-sm input-bordered w-full bg-gray-100 border-gray-300 rounded-md" value="${totalAmount || '0.00'}" readonly></td>
      <td class="whitespace-nowrap py-3 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
        <button type="button" class="remove-row text-red-600 hover:text-red-800 p-1 rounded-full hover:bg-red-100 transition-colors duration-150" title="Remove">
          <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12.56 0c.342.052.682.107 1.022.166m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.282A48.11 48.11 0 006.75 5.79" /></svg>
        </button>
      </td>
    `;
    itemsBody.appendChild(tr);
    // Set warehouse options
    updateWarehouseOptions(tr);
    recalcRow(tr);
  }

  addBtn.addEventListener('click', function () {
    addRow();
  });

  itemsBody.addEventListener('input', function (e) {
    const row = e.target.closest('.item-row');
    if (e.target.classList.contains('product')) {
      updateWarehouseOptions(row);
      recalcRow(row);
    }
    if (e.target.classList.contains('quantity')) {
      updateWarehouseOptions(row);
      recalcRow(row);
    }
  });

  itemsBody.addEventListener('change', function (e) {
    const row = e.target.closest('.item-row');
    if (e.target.classList.contains('warehouse')) {
      // Optionally, show available stock or warning
    }
  });

  itemsBody.addEventListener('click', function (e) {
    if (e.target.closest('.remove-row')) {
      e.target.closest('tr').remove();
      recalcAllTotals();
    }
  });

  // Initial setup for existing rows
  itemsBody.querySelectorAll('.item-row').forEach(row => {
    updateWarehouseOptions(row);
    recalcRow(row);
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const order = {
      date: form.date.value,
      customer: form.customer.value,
      status: form.status.value,
      paymentType: form.paymentType.value
    };
    const items = [];
    itemsBody.querySelectorAll('.item-row').forEach(row => {
      const product = row.querySelector('.product').value;
      const warehouse = row.querySelector('.warehouse').value;
      const quantity = row.querySelector('.quantity').value;
      if (product && warehouse && quantity) {
        items.push({ product, warehouse, quantity });
      }
    });
    if (items.length === 0) {
      showMessage('Please add at least one item.', true);
      return;
    }
    const url = form.dataset.update ? `/salesorders/api/${form.dataset.update}/update/` : '/salesorders/api/create/';
    fetch(url, {
      method: form.dataset.update ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ order, items })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showMessage('Order saved successfully!', false);
          setTimeout(() => { window.location.href = `/salesorders/${data.order_id}/`; }, 1000);
        } else {
          showMessage(data.error || 'An error occurred.', true);
        }
      })
      .catch(() => showMessage('An error occurred.', true));
  });

  function showMessage(msg, isError) {
    const el = document.getElementById('form-messages');
    el.textContent = msg;
    el.className = isError ? 'text-red-600 font-semibold' : 'text-green-600 font-semibold';
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
