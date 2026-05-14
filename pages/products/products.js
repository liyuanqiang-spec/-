const { products } = require('../../utils/catalog');

Page({
  data: {
    products
  },

  openDetail(event) {
    const { id } = event.currentTarget.dataset;
    wx.navigateTo({ url: `/pages/product-detail/product-detail?id=${id}` });
  },

  buyNow(event) {
    const { id } = event.currentTarget.dataset;
    getApp().globalData.cartDraft = { productId: id, quantity: 1 };
    wx.switchTab({ url: '/pages/order/order' });
  }
});
