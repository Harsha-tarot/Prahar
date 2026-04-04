Write-Host "Starting PRAHAR Backend Server..." -ForegroundColor Green
Start-Process pwsh -ArgumentList "-NoExit -Command `"cd backend; python app.py`""

Write-Host "Starting PRAHAR Frontend Server..." -ForegroundColor Green
Start-Process pwsh -ArgumentList "-NoExit -Command `"cd frontend; npm run dev`""

Write-Host "Both servers are launching in new windows." -ForegroundColor Cyan
