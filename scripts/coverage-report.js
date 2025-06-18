#!/usr/bin/env node

/**
 * Coverage Report Generator and Viewer
 *
 * This script manages code coverage reporting for the CogniticNet project,
 * including:
 * - Generating coverage reports for frontend and backend
 * - Merging coverage data from multiple sources
 * - Viewing coverage reports in the browser
 * - Uploading coverage to Codecov
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m'
};

// Utility function to execute commands
function execute(command, options = {}) {
  try {
    console.log(`${colors.dim}$ ${command}${colors.reset}`);
    execSync(command, { stdio: 'inherit', ...options });
    return true;
  } catch (error) {
    if (!options.ignoreError) {
      console.error(`${colors.red}Error executing: ${command}${colors.reset}`);
      console.error(error.message);
    }
    return false;
  }
}

// Check if a command exists
function commandExists(command) {
  try {
    execSync(`which ${command}`, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

// Generate frontend coverage
function generateFrontendCoverage() {
  console.log(`\n${colors.cyan}${colors.bright}Generating Frontend Coverage...${colors.reset}`);

  if (!fs.existsSync('package.json')) {
    console.error(`${colors.red}No package.json found. Are you in the project root?${colors.reset}`);
    return false;
  }

  return execute('npm run test:coverage');
}

// Generate backend coverage
function generateBackendCoverage() {
  console.log(`\n${colors.cyan}${colors.bright}Generating Backend Coverage...${colors.reset}`);

  if (!commandExists('coverage')) {
    console.log(`${colors.yellow}Coverage.py not found. Installing...${colors.reset}`);
    execute('pip install coverage');
  }

  // Run Python tests with coverage
  execute('coverage erase');
  const success = execute('coverage run -m pytest src/tests/', { ignoreError: true });

  if (success) {
    execute('coverage xml');
    execute('coverage html');
    execute('coverage report');
  }

  return success;
}

// Merge coverage reports
function mergeCoverageReports() {
  console.log(`\n${colors.cyan}${colors.bright}Merging Coverage Reports...${colors.reset}`);

  const coverageDir = path.join(process.cwd(), 'coverage');
  const mergedDir = path.join(coverageDir, 'merged');

  if (!fs.existsSync(mergedDir)) {
    fs.mkdirSync(mergedDir, { recursive: true });
  }

  // Check for nyc to merge coverage
  if (!commandExists('nyc')) {
    console.log(`${colors.yellow}nyc not found. Installing...${colors.reset}`);
    execute('npm install -g nyc');
  }

  // Copy frontend coverage
  const frontendLcov = path.join(coverageDir, 'lcov.info');
  if (fs.existsSync(frontendLcov)) {
    fs.copyFileSync(frontendLcov, path.join(mergedDir, 'frontend.lcov'));
  }

  // Convert Python coverage to lcov format if needed
  const pythonXml = path.join(coverageDir, 'coverage.xml');
  if (fs.existsSync(pythonXml) && commandExists('pycobertura')) {
    execute(`pycobertura convert ${pythonXml} -o ${path.join(mergedDir, 'backend.lcov')}`,
            { ignoreError: true });
  }

  console.log(`${colors.green}Coverage reports prepared for merging${colors.reset}`);
}

// View coverage report in browser
function viewCoverageReport() {
  console.log(`\n${colors.cyan}${colors.bright}Opening Coverage Report...${colors.reset}`);

  const htmlReport = path.join(process.cwd(), 'coverage', 'lcov-report', 'index.html');
  const pythonHtmlReport = path.join(process.cwd(), 'coverage', 'html', 'index.html');

  if (fs.existsSync(htmlReport)) {
    console.log(`${colors.green}Opening frontend coverage report...${colors.reset}`);
    execute(`open ${htmlReport}`, { ignoreError: true });
  } else {
    console.log(`${colors.yellow}No frontend coverage report found${colors.reset}`);
  }

  if (fs.existsSync(pythonHtmlReport)) {
    console.log(`${colors.green}Opening backend coverage report...${colors.reset}`);
    execute(`open ${pythonHtmlReport}`, { ignoreError: true });
  } else {
    console.log(`${colors.yellow}No backend coverage report found${colors.reset}`);
  }
}

// Upload coverage to Codecov
function uploadToCodecov() {
  console.log(`\n${colors.cyan}${colors.bright}Uploading to Codecov...${colors.reset}`);

  if (!process.env.CODECOV_TOKEN) {
    console.log(`${colors.yellow}No CODECOV_TOKEN found in environment${colors.reset}`);
    console.log('Coverage upload skipped. Set CODECOV_TOKEN to enable uploads.');
    return;
  }

  // Upload frontend coverage
  const frontendLcov = path.join(process.cwd(), 'coverage', 'lcov.info');
  if (fs.existsSync(frontendLcov)) {
    execute(`npx codecov -f ${frontendLcov} -F frontend`, { ignoreError: true });
  }

  // Upload backend coverage
  const backendXml = path.join(process.cwd(), 'coverage', 'coverage.xml');
  if (fs.existsSync(backendXml)) {
    execute(`npx codecov -f ${backendXml} -F backend`, { ignoreError: true });
  }
}

// Generate coverage badge
function generateCoverageBadge() {
  console.log(`\n${colors.cyan}${colors.bright}Generating Coverage Badge...${colors.reset}`);

  const coverageJson = path.join(process.cwd(), 'coverage', 'coverage-summary.json');

  if (!fs.existsSync(coverageJson)) {
    console.log(`${colors.yellow}No coverage summary found${colors.reset}`);
    return;
  }

  try {
    const summary = JSON.parse(fs.readFileSync(coverageJson, 'utf8'));
    const total = summary.total;
    const percentage = total.lines.pct;

    let color = 'red';
    if (percentage >= 80) color = 'brightgreen';
    else if (percentage >= 60) color = 'yellow';
    else if (percentage >= 40) color = 'orange';

    const badge = {
      schemaVersion: 1,
      label: 'coverage',
      message: `${percentage}%`,
      color: color
    };

    fs.writeFileSync(
      path.join(process.cwd(), 'coverage', 'badge.json'),
      JSON.stringify(badge, null, 2)
    );

    console.log(`${colors.green}Coverage badge generated: ${percentage}%${colors.reset}`);
  } catch (error) {
    console.error(`${colors.red}Error generating badge: ${error.message}${colors.reset}`);
  }
}

// Interactive menu
function showMenu() {
  console.log(`\n${colors.magenta}${colors.bright}CogniticNet Coverage Report Manager${colors.reset}`);
  console.log(`${colors.dim}${'='.repeat(40)}${colors.reset}\n`);

  console.log('1. Generate Frontend Coverage');
  console.log('2. Generate Backend Coverage');
  console.log('3. Generate All Coverage');
  console.log('4. View Coverage Reports');
  console.log('5. Upload to Codecov');
  console.log('6. Generate Coverage Badge');
  console.log('7. Full Coverage Workflow');
  console.log('0. Exit');

  rl.question('\nSelect an option: ', (answer) => {
    console.log();

    switch (answer) {
      case '1':
        generateFrontendCoverage();
        setTimeout(showMenu, 1000);
        break;

      case '2':
        generateBackendCoverage();
        setTimeout(showMenu, 1000);
        break;

      case '3':
        generateFrontendCoverage();
        generateBackendCoverage();
        mergeCoverageReports();
        setTimeout(showMenu, 1000);
        break;

      case '4':
        viewCoverageReport();
        setTimeout(showMenu, 1000);
        break;

      case '5':
        uploadToCodecov();
        setTimeout(showMenu, 1000);
        break;

      case '6':
        generateCoverageBadge();
        setTimeout(showMenu, 1000);
        break;

      case '7':
        console.log(`${colors.bright}Running full coverage workflow...${colors.reset}`);
        generateFrontendCoverage();
        generateBackendCoverage();
        mergeCoverageReports();
        generateCoverageBadge();
        uploadToCodecov();
        viewCoverageReport();
        setTimeout(showMenu, 2000);
        break;

      case '0':
        console.log(`${colors.green}Goodbye!${colors.reset}`);
        rl.close();
        process.exit(0);
        break;

      default:
        console.log(`${colors.red}Invalid option${colors.reset}`);
        showMenu();
    }
  });
}

// Command line argument handling
const args = process.argv.slice(2);

if (args.length > 0) {
  switch (args[0]) {
    case 'frontend':
      generateFrontendCoverage();
      break;
    case 'backend':
      generateBackendCoverage();
      break;
    case 'all':
      generateFrontendCoverage();
      generateBackendCoverage();
      mergeCoverageReports();
      break;
    case 'view':
      viewCoverageReport();
      break;
    case 'upload':
      uploadToCodecov();
      break;
    case 'badge':
      generateCoverageBadge();
      break;
    case 'full':
      generateFrontendCoverage();
      generateBackendCoverage();
      mergeCoverageReports();
      generateCoverageBadge();
      uploadToCodecov();
      break;
    default:
      console.log(`Unknown command: ${args[0]}`);
      console.log('Usage: coverage-report.js [frontend|backend|all|view|upload|badge|full]');
  }
  rl.close();
} else {
  // Show interactive menu
  showMenu();
}
