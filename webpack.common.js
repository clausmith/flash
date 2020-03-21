const webpack = require('webpack')
const path = require('path');
const CleanPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const ManifestPlugin = require('webpack-manifest-plugin');

const rootPath = path.resolve(__dirname)
const publicPath = process.env.ASSET_PATH || '/static/dist/'
const ctx = path.resolve(__dirname, 'app/static/src')

const config = {
  paths: {
    root: rootPath,
    assets: path.join(rootPath, 'app/static/'),
    dist: path.join(rootPath, 'app/static/dist')
  },
}

module.exports = {
  context: ctx,
  entry: {
    main: './application.js',
  },
  output: {
    path: path.resolve(__dirname, 'app/static/dist'),
    publicPath: publicPath,
    filename: `js/[name].[contenthash].js`
  },
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [[
              '@babel/preset-env',
              {
                'useBuiltIns': 'entry'
              }]],
            plugins: ['@babel/plugin-proposal-class-properties']
          }
        }
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
        ],
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader',
          'sass-loader',
        ],
      },
      {
        test: /\.(ttf|eot|woff2?|png|jpe?g|gif|svg|ico)$/,
        include: config.paths.assets,
        loader: 'file-loader',
        options: {
          limit: 4096,
          name: `[path][name].[hash].[ext]`
        },
      },
      {
        test: /\.(ttf|eot|woff2?|png|jpe?g|gif|svg|ico)$/,
        include: /node_modules/,
        loader: 'file-loader',
        options: {
          limit: 4096,
          name: `[name].[hash].[ext]`
        },
      },
    ],
  },
  resolve: {
    modules: [
      config.paths.assets,
      'node_modules',
    ],
    enforceExtension: false,
  },
  plugins: [
    new CleanPlugin(['app/static/dist']),
    new MiniCssExtractPlugin({
      filename: `css/[name].[contenthash].css`,
    }),
    new ManifestPlugin(),
    new HtmlWebpackPlugin(),
  ],
  optimization: {
    runtimeChunk: 'single',
    splitChunks: {
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        }
      }
    }
  }
};