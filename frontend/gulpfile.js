const gulp = require('gulp');
const sass = require('gulp-sass')(require('sass'));
const autoprefixer = require('gulp-autoprefixer');
const cleanCSS = require('gulp-clean-css');
const uglify = require('gulp-uglify');
const concat = require('gulp-concat');
const imagemin = require('gulp-imagemin');
const rename = require('gulp-rename');
const sourcemaps = require('gulp-sourcemaps');
const browserSync = require('browser-sync').create();
const del = require('del');
const babel = require('gulp-babel');
const eslint = require('gulp-eslint');

// Paths
const paths = {
  styles: {
    src: 'src/assets/scss/**/*.scss',
    dest: 'dist/css/'
  },
  scripts: {
    src: 'src/assets/js/**/*.js',
    dest: 'dist/js/'
  },
  images: {
    src: 'src/assets/images/**/*',
    dest: 'dist/images/'
  },
  fonts: {
    src: 'src/assets/fonts/**/*',
    dest: 'dist/fonts/'
  }
};

// Clean dist directory
function clean() {
  return del(['dist']);
}

// Compile SCSS to CSS
function styles() {
  return gulp.src(paths.styles.src)
    .pipe(sourcemaps.init())
    .pipe(sass({
      outputStyle: 'expanded',
      includePaths: ['node_modules']
    }).on('error', sass.logError))
    .pipe(autoprefixer({
      overrideBrowserslist: ['last 2 versions'],
      cascade: false
    }))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest(paths.styles.dest))
    .pipe(browserSync.stream());
}

// Minify CSS for production
function stylesMin() {
  return gulp.src(paths.styles.src)
    .pipe(sass({
      outputStyle: 'compressed',
      includePaths: ['node_modules']
    }).on('error', sass.logError))
    .pipe(autoprefixer({
      overrideBrowserslist: ['last 2 versions'],
      cascade: false
    }))
    .pipe(cleanCSS())
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest(paths.styles.dest));
}

// Lint JavaScript
function lintScripts() {
  return gulp.src(paths.scripts.src)
    .pipe(eslint())
    .pipe(eslint.format())
    .pipe(eslint.failAfterError());
}

// Process JavaScript
function scripts() {
  return gulp.src(paths.scripts.src)
    .pipe(sourcemaps.init())
    .pipe(babel({
      presets: ['@babel/env']
    }))
    .pipe(concat('main.js'))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest(paths.scripts.dest))
    .pipe(browserSync.stream());
}

// Minify JavaScript for production
function scriptsMin() {
  return gulp.src(paths.scripts.src)
    .pipe(babel({
      presets: ['@babel/env']
    }))
    .pipe(concat('main.js'))
    .pipe(uglify())
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest(paths.scripts.dest));
}

// Optimize images
function images() {
  return gulp.src(paths.images.src)
    .pipe(imagemin([
      imagemin.gifsicle({ interlaced: true }),
      imagemin.mozjpeg({ quality: 75, progressive: true }),
      imagemin.optipng({ optimizationLevel: 5 }),
      imagemin.svgo({
        plugins: [
          { removeViewBox: true },
          { cleanupIDs: false }
        ]
      })
    ]))
    .pipe(gulp.dest(paths.images.dest));
}

// Copy fonts
function fonts() {
  return gulp.src(paths.fonts.src)
    .pipe(gulp.dest(paths.fonts.dest));
}

// Watch files for changes
function watch() {
  browserSync.init({
    server: {
      baseDir: './'
    },
    port: 3001
  });
  
  gulp.watch(paths.styles.src, styles);
  gulp.watch(paths.scripts.src, gulp.series(lintScripts, scripts));
  gulp.watch(paths.images.src, images);
  gulp.watch('*.html').on('change', browserSync.reload);
}

// Development build
const dev = gulp.series(
  clean,
  gulp.parallel(styles, gulp.series(lintScripts, scripts), images, fonts)
);

// Production build
const build = gulp.series(
  clean,
  gulp.parallel(stylesMin, scriptsMin, images, fonts)
);

// Default task
const defaultTask = gulp.series(dev, watch);

// Export tasks
exports.clean = clean;
exports.styles = styles;
exports.scripts = scripts;
exports.images = images;
exports.fonts = fonts;
exports.watch = watch;
exports.dev = dev;
exports.build = build;
exports.default = defaultTask;

// Additional utility tasks
exports.lint = lintScripts;
exports['styles:min'] = stylesMin;
exports['scripts:min'] = scriptsMin;
