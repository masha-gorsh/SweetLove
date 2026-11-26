const catalog = document.getElementById('catalog');

document.querySelector('.glavnaya').addEventListener('click', function () {
  location.href = '/';
});
document.querySelector('.zapivon').addEventListener('click', function () {
  location.href = '/zapivon';
});
document.querySelector('.korzina').addEventListener('click', function () {
  location.href = '/korzina';
});


const regBtn = document.querySelector('.reegistraciya');

regBtn.addEventListener('click', function () {
  if (!regBtn.dataset.user) location.href = '/register';
});

function showUser() {
  const name = sessionStorage.getItem('userName');
  if (name) {
    regBtn.textContent = name; 
    regBtn.dataset.user = name;
  }
}

showUser();

function getCart() {
  try {
    return JSON.parse(localStorage.getItem('cart')) || [];
  } catch (e) {
    return [];
  }
}

function saveCart(cart) {
  localStorage.setItem('cart', JSON.stringify(cart));
  updateBadge();
}

function getQty(id) {
  const item = getCart().find(function (i) { return i.id === id; });
  return item ? item.qty : 0;
}

function setQty(product, qty) {
  let cart = getCart();
  const index = cart.findIndex(function (i) { return i.id === product.id; });

  if (qty <= 0) {
    if (index !== -1) cart.splice(index, 1);
  } else if (index !== -1) {
    cart[index].qty = qty;
  } else {
    cart.push({
      id: product.id,
      name: product.name,
      price: product.price,
      volume: product.volume || null,
      image: product.image,
      qty: qty
    });
  }
  saveCart(cart);
}

const cartNavBtn = document.querySelector('.korzina');
const badge = document.createElement('span');
badge.className = 'cart-badge';
cartNavBtn.appendChild(badge);

function updateBadge() {
  const total = getCart().reduce(function (sum, i) { return sum + i.qty; }, 0);
  badge.textContent = total;
  badge.style.display = total > 0 ? 'flex' : 'none';
}

updateBadge();

window.addEventListener('pageshow', function (event) {
  if (event.persisted) location.reload();
});

function createQty(count, onChange) {
  const qty = document.createElement('div');
  qty.className = 'qty';
  qty.innerHTML =
    '<button type="button" class="qty-minus">−</button>' +
    '<span class="qty-count">' + count + '</span>' +
    '<button type="button" class="qty-plus">+</button>';

  const countEl = qty.querySelector('.qty-count');

  qty.querySelector('.qty-plus').addEventListener('click', function () {
    count++;
    countEl.textContent = count;
    onChange(count);
  });

  qty.querySelector('.qty-minus').addEventListener('click', function () {
    count--;
    countEl.textContent = count;
    onChange(count);
  });

  return qty;
}

function renderCardControl(box, product) {
  box.innerHTML = '';
  const count = getQty(product.id);

  if (count > 0) {
    box.appendChild(createQty(count, function (newCount) {
      setQty(product, newCount);
      if (newCount === 0) renderCardControl(box, product);
    }));
  } else {
    const btn = document.createElement('button');
    btn.className = 'cart-btn';
    btn.textContent = 'В корзину';
    btn.addEventListener('click', function () {
      setQty(product, 1);
      renderCardControl(box, product);
    });
    box.appendChild(btn);
  }
}

function createCard(product) {
  const card = document.createElement('div');
  card.className = 'card';
  card.dataset.id = product.id;

  const img = document.createElement('img');
  img.src = product.image;
  img.alt = product.name;

  const title = document.createElement('p');
  title.className = 'card-title';
  title.textContent = product.name;

  const price = document.createElement('p');
  price.className = 'card-title';
  price.textContent = product.price + ' руб.' + (product.volume ? ' / ' + product.volume : '');

  const controls = document.createElement('div');
  controls.className = 'card-controls';
  renderCardControl(controls, product);

  card.append(img, title, price, controls);
  return card;
}

const cartForm = document.getElementById('spisok');

function renderCart() {
  const list = document.getElementById('cart-items');
  const totalEl = document.getElementById('cart-total');
  const checkoutBtn = cartForm.querySelector('.oformi-btn');
  const cart = getCart();

  list.innerHTML = '';

  if (cart.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'cart-empty';
    empty.textContent = 'Корзина пока пуста';
    list.appendChild(empty);
  }

  cart.forEach(function (item) {
    const row = document.createElement('div');
    row.className = 'cart-item';

    const img = document.createElement('img');
    img.src = item.image;
    img.alt = item.name;

    const info = document.createElement('div');
    info.className = 'cart-item-info';

    const name = document.createElement('p');
    name.className = 'spisok-title';
    name.textContent = item.name;

    const price = document.createElement('p');
    price.className = 'spisok-title';
    price.textContent = item.price + ' руб.' + (item.volume ? ' / ' + item.volume : '');

    info.append(name, price);

    const qty = createQty(item.qty, function (newCount) {
      setQty(item, newCount);
      renderCart();
    });

    row.append(img, info, qty);
    list.appendChild(row);
  });

  const total = cart.reduce(function (sum, i) { return sum + i.price * i.qty; }, 0);
  totalEl.textContent = 'Итого: ' + (Math.round(total * 100) / 100) + ' руб.';
  checkoutBtn.disabled = cart.length === 0;
}

if (cartForm) {
  renderCart();

  cartForm.addEventListener('submit', function (event) {
    event.preventDefault();
    location.href = '/oformlenie';
  });
}

let allProducts = [];

function showProducts() {
  const checked = Array.from(document.querySelectorAll('.filtr-item input:checked'))
    .map(function (input) { return input.value; });
  const sortInput = document.querySelector('input[name="sort"]:checked');
  const sort = sortInput ? sortInput.value : null;

  let list = allProducts.filter(function (p) {
    return checked.length === 0 || checked.includes(p.category);
  });

  if (sort === 'asc') list.sort(function (a, b) { return a.price - b.price; });
  if (sort === 'desc') list.sort(function (a, b) { return b.price - a.price; });

  catalog.innerHTML = '';
  if (list.length === 0) {
    catalog.textContent = 'Ничего не найдено';
    return;
  }
  list.forEach(function (product) {
    catalog.appendChild(createCard(product));
  });
}

async function loadProducts() {
  try {
    const params = new URLSearchParams();
    if (catalog.dataset.section) params.set('section', catalog.dataset.section);

    const response = await fetch('/api/products?' + params);
    if (!response.ok) throw new Error('HTTP ' + response.status);
    allProducts = await response.json();
    showProducts();
  } catch (error) {
    console.error(error);
    catalog.textContent = 'Не удалось загрузить товары. Проверь, что сервер запущен.';
  }
}

// сортировка: повторный клик по выбранной кнопке снимает сортировку
document.querySelectorAll('input[name="sort"]').forEach(function (radio) {
  radio.addEventListener('click', function () {
    if (radio.dataset.was === '1') {
      radio.checked = false;
      radio.dataset.was = '';
    } else {
      document.querySelectorAll('input[name="sort"]').forEach(function (r) { r.dataset.was = ''; });
      radio.dataset.was = '1';
    }
    showProducts();
  });
});

// фильтры: выпадающий список
const filtrBtn = document.getElementById('filtr-btn');
const filtrMenu = document.getElementById('filtr-menu');

if (filtrBtn) {
  filtrBtn.addEventListener('click', function () {
    filtrMenu.classList.toggle('open');
  });

  document.addEventListener('click', function (event) {
    if (!event.target.closest('.filtr')) filtrMenu.classList.remove('open');
  });

  filtrMenu.addEventListener('change', showProducts);
}

if (catalog) loadProducts();

const registerForm = document.getElementById('register-form');

if (registerForm) {
  registerForm.addEventListener('submit', async function (event) {
    event.preventDefault();
    const errorEl = document.getElementById('register-error');
    errorEl.textContent = '';

    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: document.getElementById('reg-name').value,
          email: document.getElementById('reg-email').value,
          password: document.getElementById('reg-password').value
        })
      });
      const data = await response.json();

      if (!response.ok) {
        errorEl.textContent = typeof data.detail === 'string'
          ? data.detail
          : 'Проверьте, что все поля заполнены, а пароль не короче 6 символов';
        return;
      }
      sessionStorage.setItem('userName', data.name);
      location.href = '/';  
    } catch (error) {
      console.error(error);
      errorEl.textContent = 'Не удалось связаться с сервером';
    }
  });
}

const loginForm = document.getElementById('login-form');

if (loginForm) {
  loginForm.addEventListener('submit', async function (event) {
    event.preventDefault();
    const errorEl = document.getElementById('login-error');
    errorEl.textContent = '';

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: document.getElementById('login-email').value,
          password: document.getElementById('login-password').value
        })
      });
      const data = await response.json();

      if (!response.ok) {
        errorEl.textContent = typeof data.detail === 'string'
          ? data.detail
          : 'Проверьте, что все поля заполнены';
        return;
      }
      sessionStorage.setItem('userName', data.name);
      location.href = '/';  
    } catch (error) {
      console.error(error);
      errorEl.textContent = 'Не удалось связаться с сервером';
    }
  });
}

const orderTotal = document.getElementById('oformlenie-total');

if (orderTotal) {
  const cart = getCart();

  if (cart.length === 0) {
    location.href = '/korzina';
  }


  const PROMOCODES = {
    '67': 50,
    'burmalda': 10,
    'avtomat': 100,
    'makscool': 150
  };

  const promoInput = document.getElementById('promo-input');
  const promoBtn = document.getElementById('promo-btn');
  const promoMessage = document.getElementById('promo-message');

  const baseTotal = Math.round(
    cart.reduce(function (sum, i) { return sum + i.price * i.qty; }, 0) * 100
  ) / 100;
  let discountPercent = 0;

  function showTotal() {
    const finalTotal = Math.round(baseTotal * (1 - discountPercent / 100) * 100) / 100;

    if (finalTotal < 0) {
      orderTotal.textContent = 'Поздравляем! Вам дадут: ' + (-finalTotal) + ' руб.';
    } else if (discountPercent > 0) {
      orderTotal.textContent = 'Итого: ' + finalTotal + ' руб. (без скидки ' + baseTotal + ' руб.)';
    } else {
      orderTotal.textContent = 'Итого: ' + baseTotal + ' руб.';
    }
  }

  function applyPromo() {
    const code = promoInput.value.trim().toLowerCase();
    promoMessage.classList.remove('error');

    if (code === '') {
      discountPercent = 0;
      promoMessage.textContent = '';
    } else if (PROMOCODES[code] !== undefined) {
      discountPercent = PROMOCODES[code];
      promoMessage.textContent = 'Промокод применён!';
    } else {
      discountPercent = 0;
      promoMessage.textContent = 'айайай Такого промокода нет';
      promoMessage.classList.add('error');
    }
    showTotal();
  }

  promoBtn.addEventListener('click', applyPromo);

  // Enter в поле промокода применяет его, а не отправляет заказ
  promoInput.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      applyPromo();
    }
  });

  document.getElementById('oformlenie').addEventListener('submit', function (event) {
    event.preventDefault();
    // TODO: сюда позже добавим отправку заказа
  });

  showTotal();
}
