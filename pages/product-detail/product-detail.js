const { findProduct } = require('../../utils/catalog');

Page({
  data: {
    product: null
  },

  onLoad(options) {
    this.setData({ product: findProduct(options.id) });
  },

  buyNow() {
    getApp().globalData.cartDraft = {
      productId: this.data.product.id,
      quantity: 1
    };
    wx.switchTab({ url: '/pages/order/order' });
  }
});
