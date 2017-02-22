
////////////////////////////////
		//Setup//
////////////////////////////////

// Plugins
var gulp = require('gulp'),
      pjson = require('./package.json'),
      gutil = require('gulp-util'),
      sass = require('gulp-sass'),
      autoprefixer = require('gulp-autoprefixer'),
      cssnano = require('gulp-cssnano'),
      rename = require('gulp-rename'),
      del = require('del'),
      plumber = require('gulp-plumber'),
      pixrem = require('gulp-pixrem'),
      uglify = require('gulp-uglify'),
      imagemin = require('gulp-imagemin'),
      exec = require('child_process').exec,
      runSequence = require('run-sequence'),
      browserSync = require('browser-sync').create(),
      reload = browserSync.reload,
      semanticConfig       = require('./tempo/static/semantic/tasks/config/user'),
      // watch changes
      semanticWatch        = require('./tempo/static/semantic/tasks/watch'),

      // build all files
      semanticBuild        = require('./tempo/static/semantic/tasks/build'),
      semanticBuildJS      = require('./tempo/static/semantic/tasks/build/javascript'),
      semanticBuildCSS     = require('./tempo/static/semantic/tasks/build/css'),
      semanticBuildAssets  = require('./tempo/static/semantic/tasks/build/assets'),

      // utility
      semanticClean        = require('./tempo/static/semantic/tasks/clean'),
      semanticVersion      = require('./tempo/static/semantic/tasks/version'),

      // docs tasks
      semanticServeDocs    = require('./tempo/static/semantic/tasks/docs/serve'),
      semanticBuildDocs    = require('./tempo/static/semantic/tasks/docs/build'),

      // rtl
      semanticBuildRTL     = require('./tempo/static/semantic/tasks/rtl/build'),
      semanticWatchRTL     = require('./tempo/static/semantic/tasks/rtl/watch')
      ;


        /*******************************
                   Tasks
      *******************************/

      gulp.task('semantic-watch', 'Watch for site/theme changes', semanticWatch);

      gulp.task('semantic-build', 'Builds all files from source', semanticBuild);
      gulp.task('semantic-build-javascript', 'Builds all javascript from source', semanticBuildJS);
      gulp.task('semantic-build-css', 'Builds all css from source', semanticBuildCSS);
      gulp.task('semantic-build-assets', 'Copies all assets from source', semanticBuildAssets);

      gulp.task('semantic-clean', 'Clean dist folder', semanticClean);
      gulp.task('semantic-version', 'Displays current version of Semantic', semanticVersion);

      /*--------------
            Docs
      ---------------*/

      /*
        Lets you serve files to a local documentation instance
        https://github.com/Semantic-Org/Semantic-UI-Docs/
      */

      gulp.task('semantic-serve-docs', 'Serve file changes to SUI Docs', semanticServeDocs);
      gulp.task('semantic-build-docs', 'Build all files and add to SUI Docs', semanticBuildDocs);


      /*--------------
            RTL
      ---------------*/

      if(semanticConfig.rtl) {
        gulp.task('semantic-watch-rtl', 'Watch files as RTL', semanticWatchRTL);
        gulp.task('semantic-build-rtl', 'Build all files as RTL', semanticBuildRTL);
      }

// Relative paths function
var pathsConfig = function (appName) {
  this.app = "./" + (appName || pjson.name);

  return {
    app: this.app,
    templates: this.app + '/templates',
    css: this.app + '/static/css',
    sass: this.app + '/static/sass',
    fonts: this.app + '/static/fonts',
    images: this.app + '/static/images',
    js: this.app + '/static/js',
  }
};

var paths = pathsConfig();

////////////////////////////////
		//Tasks//
////////////////////////////////

// Styles autoprefixing and minification
gulp.task('styles', function() {
  return gulp.src(paths.sass + '/project.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(plumber()) // Checks for errors
    .pipe(autoprefixer({browsers: ['last 2 version']})) // Adds vendor prefixes
    .pipe(pixrem())  // add fallbacks for rem units
    .pipe(gulp.dest(paths.css))
    .pipe(rename({ suffix: '.min' }))
    .pipe(cssnano()) // Minifies the result
    .pipe(gulp.dest(paths.css));
});

// Javascript minification
gulp.task('scripts', function() {
  return gulp.src(paths.js + '/project.js')
    .pipe(plumber()) // Checks for errors
    .pipe(uglify()) // Minifies the js
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest(paths.js));
});

// Image compression
gulp.task('imgCompression', function(){
  return gulp.src(paths.images + '/*')
    .pipe(imagemin()) // Compresses PNG, JPEG, GIF and SVG images
    .pipe(gulp.dest(paths.images))
});

// Run django server
gulp.task('runServer', function() {
  exec('python manage.py runserver', function (err, stdout, stderr) {
    console.log(stdout);
    console.log(stderr);
  });
});

// Browser sync server for live reload
gulp.task('browserSync', function() {
    browserSync.init(
      [paths.css + "/*.css", paths.js + "*.js", paths.templates + '*.html'], {
        proxy:  "localhost:8000"
    });
});

// Watch
gulp.task('watch', function() {

  gulp.watch(paths.sass + '/*.scss', ['styles']);
  gulp.watch(paths.js + '/*.js', ['scripts']).on("change", reload);
  gulp.watch(paths.images + '/*', ['imgCompression']);
  gulp.watch(paths.templates + '/**/*.html').on("change", reload);

});

// Default task
gulp.task('default', function() {
    runSequence(['styles', 'scripts', 'imgCompression'], 'runServer', 'browserSync', 'semantic-watch', 'watch');
});
