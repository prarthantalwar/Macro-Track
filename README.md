MacroTrack App for daily macro tracking

```
Macro Track
├─ .gitignore
├─ app.py
├─ database.py
├─ db.sql
├─ README.md
├─ requirements.txt
├─ static
│  ├─ css
│  │  ├─ bootstrap-theme.css
│  │  ├─ bootstrap-theme.css.map
│  │  ├─ bootstrap-theme.min.css
│  │  ├─ bootstrap-theme.min.css.map
│  │  ├─ bootstrap.css
│  │  ├─ bootstrap.css.map
│  │  ├─ bootstrap.min.css
│  │  ├─ bootstrap.min.css.map
│  │  ├─ cerulean.min.css
│  │  ├─ flatly.min.css
│  │  ├─ style.css
│  │  ├─ style.css.map
│  │  ├─ styles.css
│  │  └─ united.min.css
│  ├─ favicon
│  │  ├─ android-chrome-192x192.png
│  │  ├─ android-chrome-512x512.png
│  │  ├─ apple-touch-icon.png
│  │  ├─ favicon-16x16.png
│  │  ├─ favicon-32x32.png
│  │  ├─ favicon.ico
│  │  └─ site.webmanifest
│  ├─ fonts
│  │  ├─ glyphicons-halflings-regular.eot
│  │  ├─ glyphicons-halflings-regular.svg
│  │  ├─ glyphicons-halflings-regular.ttf
│  │  ├─ glyphicons-halflings-regular.woff
│  │  ├─ glyphicons-halflings-regular.woff2
│  │  ├─ material-icon
│  │  │  ├─ css
│  │  │  │  ├─ material-design-iconic-font.css
│  │  │  │  └─ material-design-iconic-font.min.css
│  │  │  └─ fonts
│  │  │     ├─ Material-Design-Iconic-Font.eot
│  │  │     ├─ Material-Design-Iconic-Font.svg
│  │  │     ├─ Material-Design-Iconic-Font.ttf
│  │  │     ├─ Material-Design-Iconic-Font.woff
│  │  │     └─ Material-Design-Iconic-Font.woff2
│  │  └─ poppins
│  │     ├─ poppins-v5-latin-300.eot
│  │     ├─ poppins-v5-latin-300.svg
│  │     ├─ poppins-v5-latin-300.ttf
│  │     ├─ poppins-v5-latin-300.woff
│  │     ├─ poppins-v5-latin-300.woff2
│  │     ├─ poppins-v5-latin-300italic.eot
│  │     ├─ poppins-v5-latin-300italic.svg
│  │     ├─ poppins-v5-latin-300italic.ttf
│  │     ├─ poppins-v5-latin-300italic.woff
│  │     ├─ poppins-v5-latin-300italic.woff2
│  │     ├─ poppins-v5-latin-500.eot
│  │     ├─ poppins-v5-latin-500.svg
│  │     ├─ poppins-v5-latin-500.ttf
│  │     ├─ poppins-v5-latin-500.woff
│  │     ├─ poppins-v5-latin-500.woff2
│  │     ├─ poppins-v5-latin-500italic.eot
│  │     ├─ poppins-v5-latin-500italic.svg
│  │     ├─ poppins-v5-latin-500italic.ttf
│  │     ├─ poppins-v5-latin-500italic.woff
│  │     ├─ poppins-v5-latin-500italic.woff2
│  │     ├─ poppins-v5-latin-600.eot
│  │     ├─ poppins-v5-latin-600.svg
│  │     ├─ poppins-v5-latin-600.ttf
│  │     ├─ poppins-v5-latin-600.woff
│  │     ├─ poppins-v5-latin-600.woff2
│  │     ├─ poppins-v5-latin-700.eot
│  │     ├─ poppins-v5-latin-700.svg
│  │     ├─ poppins-v5-latin-700.ttf
│  │     ├─ poppins-v5-latin-700.woff
│  │     ├─ poppins-v5-latin-700.woff2
│  │     ├─ poppins-v5-latin-700italic.eot
│  │     ├─ poppins-v5-latin-700italic.svg
│  │     ├─ poppins-v5-latin-700italic.ttf
│  │     ├─ poppins-v5-latin-700italic.woff
│  │     ├─ poppins-v5-latin-700italic.woff2
│  │     ├─ poppins-v5-latin-800.eot
│  │     ├─ poppins-v5-latin-800.svg
│  │     ├─ poppins-v5-latin-800.ttf
│  │     ├─ poppins-v5-latin-800.woff
│  │     ├─ poppins-v5-latin-800.woff2
│  │     ├─ poppins-v5-latin-800italic.eot
│  │     ├─ poppins-v5-latin-800italic.svg
│  │     ├─ poppins-v5-latin-800italic.ttf
│  │     ├─ poppins-v5-latin-800italic.woff
│  │     ├─ poppins-v5-latin-800italic.woff2
│  │     ├─ poppins-v5-latin-900.eot
│  │     ├─ poppins-v5-latin-900.svg
│  │     ├─ poppins-v5-latin-900.ttf
│  │     ├─ poppins-v5-latin-900.woff
│  │     ├─ poppins-v5-latin-900.woff2
│  │     ├─ poppins-v5-latin-italic.eot
│  │     ├─ poppins-v5-latin-italic.svg
│  │     ├─ poppins-v5-latin-italic.ttf
│  │     ├─ poppins-v5-latin-italic.woff
│  │     ├─ poppins-v5-latin-italic.woff2
│  │     ├─ poppins-v5-latin-regular.eot
│  │     ├─ poppins-v5-latin-regular.svg
│  │     ├─ poppins-v5-latin-regular.ttf
│  │     ├─ poppins-v5-latin-regular.woff
│  │     ├─ poppins-v5-latin-regular.woff2
│  │     ├─ roboto-condensed-v16-latin-700.eot
│  │     ├─ roboto-condensed-v16-latin-700.svg
│  │     ├─ roboto-condensed-v16-latin-700.ttf
│  │     ├─ roboto-condensed-v16-latin-700.woff
│  │     ├─ roboto-condensed-v16-latin-700.woff2
│  │     ├─ roboto-condensed-v16-latin-700italic.eot
│  │     ├─ roboto-condensed-v16-latin-700italic.svg
│  │     ├─ roboto-condensed-v16-latin-700italic.ttf
│  │     ├─ roboto-condensed-v16-latin-700italic.woff
│  │     ├─ roboto-condensed-v16-latin-700italic.woff2
│  │     ├─ roboto-condensed-v16-latin-italic.eot
│  │     ├─ roboto-condensed-v16-latin-italic.svg
│  │     ├─ roboto-condensed-v16-latin-italic.ttf
│  │     ├─ roboto-condensed-v16-latin-italic.woff
│  │     ├─ roboto-condensed-v16-latin-italic.woff2
│  │     ├─ roboto-condensed-v16-latin-regular.eot
│  │     ├─ roboto-condensed-v16-latin-regular.svg
│  │     ├─ roboto-condensed-v16-latin-regular.ttf
│  │     ├─ roboto-condensed-v16-latin-regular.woff
│  │     └─ roboto-condensed-v16-latin-regular.woff2
│  ├─ images
│  │  ├─ signin-image.jpg
│  │  └─ signup-image.jpg
│  ├─ img
│  │  └─ bg.jpg
│  ├─ js
│  │  ├─ bootstrap.js
│  │  ├─ bootstrap.min.js
│  │  ├─ jquery.min.js
│  │  ├─ main.js
│  │  └─ npm.js
│  ├─ scss
│  │  ├─ common
│  │  │  ├─ extend.scss
│  │  │  ├─ fonts.scss
│  │  │  ├─ global.scss
│  │  │  ├─ minxi.scss
│  │  │  └─ variables.scss
│  │  ├─ layouts
│  │  │  ├─ main.scss
│  │  │  └─ responsive.scss
│  │  └─ style.scss
│  └─ vendor
│     └─ jquery
│        ├─ jquery-ui.min.js
│        └─ jquery.min.js
└─ templates
   ├─ add.html
   ├─ index.html
   ├─ signin.html
   ├─ signup.html
   └─ view.html

```

Avoid duplicates everywhere, foods, dates etc.
Display appropriate message with flashes not redirects.
Improve UI
Work on remember me function, it didn't log me out when I closed a tab without clicking remember me
