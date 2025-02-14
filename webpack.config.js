const path = require('path');
const webpack = require('webpack');

module.exports = {
  // Entry point for your application
  entry: './src/index.js',

  // Output configuration
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
    publicPath: '/',
  },

  // Module rules for processing different file types
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },

  // Resolve configuration for handling Node.js globals
  resolve: {
    fallback: {
      "process": require.resolve("process/browser"),
      "buffer": require.resolve("buffer/"),
      "util": require.resolve("util/"),
      "stream": require.resolve("stream-browserify"),
      "assert": require.resolve("assert/"),
      "crypto": require.resolve("crypto-browserify"),
      "http": require.resolve("stream-http"),
      "https": require.resolve("https-browserify"),
      "os": require.resolve("os-browserify/browser"),
      "path": require.resolve("path-browserify"),
    },
  },

  // Plugins for providing Node.js globals
  plugins: [
    new webpack.ProvidePlugin({
      process: 'process/browser',
      Buffer: ['buffer', 'Buffer'],
    }),
  ],

  // Enable source maps for debugging
  devtool: 'source-map',

  // Development server configuration
  devServer: {
    static: path.join(__dirname, 'dist'),
    hot: true,
    historyApiFallback: true,
  },
};