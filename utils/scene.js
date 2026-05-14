function decodeScene(rawScene = '') {
  if (!rawScene) {
    return {
      source: 'direct',
      code: '',
      label: '自然访问'
    };
  }

  const decoded = decodeURIComponent(rawScene);
  const pairs = decoded.split('&').reduce((result, part) => {
    const [key, value = ''] = part.split('=');
    if (key) {
      result[key] = value;
    }
    return result;
  }, {});

  return {
    source: pairs.src || pairs.source || 'qr',
    code: pairs.code || pairs.store || pairs.guide || decoded,
    label: pairs.name || pairs.label || '扫码渠道'
  };
}

module.exports = {
  decodeScene
};
