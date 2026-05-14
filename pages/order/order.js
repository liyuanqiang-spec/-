const { products, findProduct } = require('../../utils/catalog');

Page({
  data: {
    products,
    productNames: products.map((item) => item.name),
    selectedIndex: 0,
    product: products[0],
    total: products[0].price,
    channel: {},
    form: {
      quantity: 1,
      name: '',
      phone: '',
      city: '',
      address: '',
      documentTail: '',
      remark: ''
    }
  },

  onShow() {
    const draft = getApp().globalData.cartDraft;
    const product = draft ? findProduct(draft.productId) : this.data.product;
    const selectedIndex = products.findIndex((item) => item.id === product.id);
    const quantity = draft ? draft.quantity : this.data.form.quantity;

    this.setData({
      product,
      selectedIndex: selectedIndex > -1 ? selectedIndex : 0,
      channel: getApp().getChannel(),
      'form.quantity': quantity
    });
    this.calculateTotal();
  },

  selectProduct(event) {
    const selectedIndex = Number(event.detail.value);
    this.setData({
      selectedIndex,
      product: products[selectedIndex]
    });
    this.calculateTotal();
  },

  updateField(event) {
    const { field } = event.currentTarget.dataset;
    this.setData({ [`form.${field}`]: event.detail.value });
  },

  decrease() {
    const quantity = Math.max(1, this.data.form.quantity - 1);
    this.setData({ 'form.quantity': quantity });
    this.calculateTotal();
  },

  increase() {
    const quantity = Math.min(20, this.data.form.quantity + 1);
    this.setData({ 'form.quantity': quantity });
    this.calculateTotal();
  },

  calculateTotal() {
    this.setData({ total: this.data.product.price * this.data.form.quantity });
  },

  submitOrder() {
    const { form, product, total, channel } = this.data;
    if (!form.name || !form.phone || !form.city || !form.address) {
      wx.showToast({ title: '请完善收货信息', icon: 'none' });
      return;
    }

    const order = {
      id: `MY${Date.now()}`,
      productId: product.id,
      productName: product.name,
      total,
      channel,
      consignee: form,
      status: 'draft_waiting_service_confirm'
    };
    wx.setStorageSync('lastOrder', order);
    wx.showModal({
      title: '订单草稿已生成',
      content: `订单号 ${order.id}。下一步可对接微信支付、客服复核和国内仓发货。`,
      showCancel: false
    });
  }
});
