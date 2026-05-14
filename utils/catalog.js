const products = [
  {
    id: 'skin-001',
    name: '国货修护精华礼盒',
    subtitle: '适合游客回购的轻量护肤套装',
    price: 299,
    marketPrice: 399,
    currency: 'CNY',
    stock: 86,
    origin: '杭州保税/国内仓',
    shipping: '中国仓发货，预计 7-12 天送达马来西亚主要城市',
    tags: ['热卖', '可回购', '轻便'],
    cover: 'https://dummyimage.com/720x520/0f766e/ffffff&text=Skin+Care',
    detail: [
      '适合旅途中体验后复购，礼盒包装便于送礼。',
      '支持微信客服确认肤质与使用方法。',
      '下单后由国内仓打包，提供物流追踪。'
    ]
  },
  {
    id: 'tea-002',
    name: '云南古树滇红茶伴手礼',
    subtitle: '小罐独立包装，适合送亲友',
    price: 168,
    marketPrice: 238,
    currency: 'CNY',
    stock: 120,
    origin: '云南昆明仓',
    shipping: '中国仓发货，预计 8-14 天送达马来西亚',
    tags: ['伴手礼', '轻抛货', '中文客服'],
    cover: 'https://dummyimage.com/720x520/f59e0b/ffffff&text=Chinese+Tea',
    detail: [
      '每罐独立密封，方便游客按件购买。',
      '适合门店试饮后扫码回购。',
      '可配置节日礼袋与企业团购价。'
    ]
  },
  {
    id: 'health-003',
    name: '便携艾草足浴包 30 袋',
    subtitle: '低客单、高复购的家庭养生产品',
    price: 89,
    marketPrice: 129,
    currency: 'CNY',
    stock: 240,
    origin: '广东佛山仓',
    shipping: '中国仓发货，预计 7-10 天送达吉隆坡/槟城/新山',
    tags: ['家庭装', '复购款', '中文说明'],
    cover: 'https://dummyimage.com/720x520/16a34a/ffffff&text=Wellness',
    detail: [
      '轻便不易碎，适合跨境小包。',
      '包装内含中文与英文使用说明。',
      '适合旅行社、门店、展会渠道推广。'
    ]
  }
];

function findProduct(productId) {
  return products.find((item) => item.id === productId) || products[0];
}

module.exports = {
  products,
  findProduct
};
