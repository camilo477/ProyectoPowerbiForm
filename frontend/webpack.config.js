const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/pages/blog.html', // usa tu HTML como plantilla
      filename: 'blog.html' // nombre del archivo final
    })
  ]
};
