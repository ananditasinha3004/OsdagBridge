CORRECTED TASK 1 PACKAGE, VERSION 2

Open PACKAGE_INDEX.csv for all 17 cases and their exact file locations.
reports/Task1_TC01_TC17_Test_Report.pdf covers TC01 through TC17.
reports/TC01_Test_Report.pdf through TC17_Test_Report.pdf are individual test reports.
osi/ contains all 17 case inputs. screenshots/ contains images for all 17 cases.
results/ contains all 17 native workbooks. runs/ contains TC01 through TC17.
logs/ contains the recorded execution logs indexed in PACKAGE_INDEX.csv.

TC01 ORIGINAL LOG LIMITATION:
The original manual TC01 runtime log and output dictionary were never captured.
The original screenshots, OSI and workbook are preserved in runs/TC01/original.
A new TC01 execution captured a real runtime log and dictionaries under
runs/TC01/replay1. Its timestamp and provenance are explicit; it is not passed
off as the original run. TC02's original final log is logs/TC02_final.log.

These PDFs are testing reports, not application-generated full structural
design reports. Native full design-report PDFs remain outside this package.
Execution completion does not mean structural checks passed. Previously
documented input-retention and export findings remain unresolved.

The root category folders provide convenient copies of case evidence. The
same bytes may also appear inside runs/ for self-contained case records.
MANIFEST_SHA256.txt hashes all bundled files except the manifest itself.
The previous package is retained as Task1_TC01_TC17_Evidence_v1.zip.
