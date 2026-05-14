App({
  globalData: {
    channel: {
      source: 'direct',
      code: '',
      label: '自然访问'
    },
    cartDraft: null
  },

  setChannel(channel) {
    this.globalData.channel = channel;
    wx.setStorageSync('channel', channel);
  },

  getChannel() {
    return wx.getStorageSync('channel') || this.globalData.channel;
  }
});
