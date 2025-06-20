module.exports = {
  testEnvironment: "node",
  testMatch: [
    "**/__tests__/**/*.(js|jsx|ts|tsx)",
    "**/*.(test|spec).(js|jsx|ts|tsx)",
  ],
  collectCoverageFrom: ["src/**/*.(js|jsx|ts|tsx)", "!src/**/*.d.ts"],
  coverageDirectory: "coverage",
  coverageReporters: ["text", "lcov", "html"],
  testTimeout: 300000,
  maxWorkers: 4,
  verbose: false,
  reporters: [
    "default",
    [
      "jest-junit",
      {
        outputDirectory: "test-results",
        outputName: "jest-results.xml",
      },
    ],
  ],
};
