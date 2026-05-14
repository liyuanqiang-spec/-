const { decodeScene } = require('../../utils/scene');

Page({
  data: {
    channel: {},
    steps: [
      {
        title: '扫码进入',
        desc: '游客扫描门店、导游或展台二维码，自动记录渠道来源。'
      },
      {
        title: '浏览商品',
        desc: '展示适合跨境配送的轻便爆品、发货地、预计时效与售后说明。'
      },
      {
        title: '提交订单',
        desc: '填写马来西亚地址、WhatsApp/手机号，由客服复核后安排中国仓发货。'
      }
    ]
  },

  onLoad(options) {
    const app = getApp();
    const channel = decodeScene(options.scene);
    app.setChannel(channel);
    this.setData({ channel });
  },

  onShow() {
    this.setData({ channel: getApp().getChannel() });
  },

  goProducts() {
    wx.switchTab({ url: '/pages/products/products' });
  },

  scanCode() {
    wx.scanCode({
      success: (res) => {
        const scene = res.path ? (res.path.split('scene=')[1] || res.result) : res.result;
        const channel = decodeScene(scene);
        getApp().setChannel(channel);
        this.setData({ channel });
        wx.showToast({ title: '渠道已记录', icon: 'success' });
      },
      fail: () => {
        wx.showToast({ title: '未完成扫码', icon: 'none' });
      }
    });
  }
});
