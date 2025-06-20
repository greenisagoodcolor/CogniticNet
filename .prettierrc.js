module.exports = {
  // Line width
  printWidth: 100,

  // Indentation
  tabWidth: 2,
  useTabs: false,

  // Semicolons
  semi: true,

  // Quotes
  singleQuote: true,
  quoteProps: "as-needed",

  // JSX quotes
  jsxSingleQuote: false,

  // Trailing commas
  trailingComma: "es5",

  // Brackets
  bracketSpacing: true,
  bracketSameLine: false,

  // Arrow functions
  arrowParens: "always",

  // Line endings
  endOfLine: "lf",

  // HTML whitespace sensitivity
  htmlWhitespaceSensitivity: "css",

  // Vue files script and style tags indentation
  vueIndentScriptAndStyle: false,

  // Embedded language formatting
  embeddedLanguageFormatting: "auto",

  // Single attribute per line in HTML, Vue and JSX
  singleAttributePerLine: false,

  // Prose wrap
  proseWrap: "preserve",

  // Require pragma
  requirePragma: false,
  insertPragma: false,

  // Override for specific file types
  overrides: [
    {
      files: ["*.json", "*.jsonc"],
      options: {
        printWidth: 80,
        trailingComma: "none",
      },
    },
    {
      files: "*.md",
      options: {
        proseWrap: "always",
        printWidth: 80,
      },
    },
    {
      files: ["*.yml", "*.yaml"],
      options: {
        singleQuote: false,
      },
    },
    {
      files: ["*.css", "*.scss", "*.less"],
      options: {
        singleQuote: false,
      },
    },
  ],

  // Tailwind CSS plugin configuration
  plugins: ["prettier-plugin-tailwindcss"],
  tailwindConfig: "./tailwind.config.ts",
  tailwindFunctions: ["clsx", "cn", "twMerge"],
};
