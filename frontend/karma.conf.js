// Karma configuration
module.exports = function(config) {
  config.set({
    // Base path that will be used to resolve all patterns (e.g. files, exclude)
    basePath: '',

    // Frameworks to use
    // Available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine', 'webpack'],

    // List of files / patterns to load in the browser
    files: [
      'src/**/*.spec.js',
      'src/**/*.test.js',
      'tests/**/*.spec.js',
      'tests/**/*.test.js'
    ],

    // List of files / patterns to exclude
    exclude: [
      'node_modules/**',
      'dist/**',
      'build/**'
    ],

    // Preprocess matching files before serving them to the browser
    // Available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
      'src/**/*.js': ['webpack', 'sourcemap'],
      'src/**/*.jsx': ['webpack', 'sourcemap'],
      'tests/**/*.js': ['webpack', 'sourcemap'],
      'tests/**/*.jsx': ['webpack', 'sourcemap']
    },

    // Webpack configuration
    webpack: {
      mode: 'development',
      module: {
        rules: [
          {
            test: /\.(js|jsx)$/,
            exclude: /node_modules/,
            use: {
              loader: 'babel-loader',
              options: {
                presets: ['@babel/preset-env', '@babel/preset-react']
              }
            }
          },
          {
            test: /\.css$/,
            use: ['style-loader', 'css-loader']
          },
          {
            test: /\.scss$/,
            use: ['style-loader', 'css-loader', 'sass-loader']
          },
          {
            test: /\.(png|jpe?g|gif|svg)$/i,
            use: [
              {
                loader: 'file-loader',
                options: {
                  name: '[path][name].[ext]'
                }
              }
            ]
          }
        ]
      },
      resolve: {
        extensions: ['.js', '.jsx', '.json']
      },
      devtool: 'inline-source-map'
    },

    // Webpack middleware configuration
    webpackMiddleware: {
      stats: 'errors-only'
    },

    // Test results reporter to use
    // Possible values: 'dots', 'progress', 'junit', 'growl', 'coverage'
    reporters: ['progress', 'coverage', 'junit'],

    // Coverage reporter configuration
    coverageReporter: {
      type: 'html',
      dir: 'coverage/',
      subdir: '.',
      reporters: [
        { type: 'html', subdir: 'html' },
        { type: 'lcov', subdir: 'lcov' },
        { type: 'text-summary' }
      ]
    },

    // JUnit reporter configuration
    junitReporter: {
      outputDir: 'test-results/',
      outputFile: 'test-results.xml',
      suite: 'InvestWise Frontend Tests',
      useBrowserName: false
    },

    // Web server port
    port: 9876,

    // Enable / disable colors in the output (reporters and logs)
    colors: true,

    // Level of logging
    // Possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,

    // Enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,

    // Start these browsers
    // Available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['Chrome', 'ChromeHeadless'],

    // Custom browser configurations
    customLaunchers: {
      ChromeHeadlessCI: {
        base: 'ChromeHeadless',
        flags: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-gpu',
          '--disable-dev-shm-usage',
          '--remote-debugging-port=9222'
        ]
      }
    },

    // Continuous Integration mode
    // If true, Karma captures browsers, runs the tests and exits
    singleRun: false,

    // Concurrency level
    // How many browser will be started simultaneously
    concurrency: Infinity,

    // Browser timeout settings
    browserDisconnectTimeout: 10000,
    browserDisconnectTolerance: 3,
    browserNoActivityTimeout: 60000,

    // Client configuration
    client: {
      captureConsole: true,
      clearContext: false,
      runInParent: false,
      useIframe: true,
      jasmine: {
        random: true,
        seed: '4321',
        stopOnSpecFailure: false,
        failFast: false,
        timeoutInterval: 30000
      }
    },

    // Plugin configuration
    plugins: [
      'karma-jasmine',
      'karma-webpack',
      'karma-chrome-launcher',
      'karma-coverage',
      'karma-junit-reporter',
      'karma-sourcemap-loader'
    ]
  });
};
