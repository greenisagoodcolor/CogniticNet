#!/bin/bash

# View Coverage Reports Script
# This script opens the HTML coverage reports in your browser

echo "🔍 CogniticNet Coverage Report Viewer"
echo "===================================="

# Check if we're in the project root
if [ ! -f "package.json" ]; then
    echo "❌ Error: Not in project root directory"
    exit 1
fi

# Frontend coverage report
FRONTEND_REPORT="coverage/lcov-report/index.html"
BACKEND_REPORT="coverage/html/index.html"

opened=false

# Check and open frontend coverage
if [ -f "$FRONTEND_REPORT" ]; then
    echo "✅ Opening frontend coverage report..."
    open "$FRONTEND_REPORT"
    opened=true
else
    echo "⚠️  No frontend coverage report found"
    echo "   Run 'npm run test:coverage' to generate"
fi

# Check and open backend coverage
if [ -f "$BACKEND_REPORT" ]; then
    echo "✅ Opening backend coverage report..."
    open "$BACKEND_REPORT"
    opened=true
else
    echo "⚠️  No backend coverage report found"
    echo "   Run 'coverage run -m pytest && coverage html' to generate"
fi

# If no reports found
if [ "$opened" = false ]; then
    echo ""
    echo "📝 To generate coverage reports:"
    echo "   - Frontend: npm run test:coverage"
    echo "   - Backend:  make coverage"
    echo "   - Both:     make coverage-full"
    exit 1
fi

echo ""
echo "✨ Coverage reports opened in browser"
