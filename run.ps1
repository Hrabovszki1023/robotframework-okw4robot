# Temporär Execution Policy lockern
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Virtuelle Umgebung aktivieren
. .venv\Scripts\Activate.ps1

# Projekt installieren (editable)
pip install -e .

# Robot-Tests ausführen
# robot -d reports tests\test_swingset3_structure.robot
robot -d reports `
  tests\WidgetsDemo.robot `
  tests\Web_Caption.robot `
  tests\Web_Label.robot `
  tests\Web_Placeholder.robot `
  tests\Web_Attribute.robot `
  tests\Web_Focus.robot `
  tests\Web_VerifyExist.robot `
  tests\Web_VerifyVisible.robot `
  tests\Web_VerifyEnabled.robot `
  tests\Web_VerifyEditable.robot `
  tests\Web_VerifyFocusable.robot `
  tests\Web_VerifyClickable.robot `
  tests\Web_VerifyHasFocus.robot `
  tests\Web_Table_VerifyCell.robot `
  tests\Web_Table_VerifyRow.robot `
  tests\Web_Table_VerifyColumn.robot `
  tests\Web_Table_VerifyCounts.robot `
  tests\Web_Table_VerifyHasRow.robot `
  tests\Web_Table_VerifyContent.robot `
  tests\Web_Table_VerifyByHeaders.robot `
  tests\Web_Table_VerifyByHeadersREGX.robot `
  tests\Web_List_VerifyCounts.robot
