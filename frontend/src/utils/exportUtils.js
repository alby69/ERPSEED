import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

export async function exportToPng(elementRef, filename = 'dashboard') {
  if (!elementRef) {
    throw new Error('Element reference is required');
  }

  const canvas = await html2canvas(elementRef, {
    scale: 2,
    useCORS: true,
    logging: false,
    backgroundColor: '#ffffff',
  });

  const link = document.createElement('a');
  link.download = `${filename}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
}

export async function exportToPdf(elementRef, filename = 'dashboard', orientation = 'landscape') {
  if (!elementRef) {
    throw new Error('Element reference is required');
  }

  const canvas = await html2canvas(elementRef, {
    scale: 2,
    useCORS: true,
    logging: false,
    backgroundColor: '#ffffff',
  });

  const imgData = canvas.toDataURL('image/png');
  const pdf = new jsPDF({
    orientation,
    unit: 'mm',
    format: 'a4',
  });

  const imgWidth = orientation === 'landscape' ? 297 : 210;
  const pageHeight = orientation === 'landscape' ? 210 : 297;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;

  let heightLeft = imgHeight;
  let position = 0;

  pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
  heightLeft -= pageHeight;

  while (heightLeft > 0) {
    position = heightLeft - imgHeight;
    pdf.addPage();
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;
  }

  pdf.save(`${filename}.pdf`);
}

export async function exportToImage(elementRef, format = 'png', options = {}) {
  const { filename = 'export', ...pdfOptions } = options;

  if (format === 'pdf') {
    return exportToPdf(elementRef, filename, pdfOptions.orientation);
  }

  return exportToPng(elementRef, filename);
}
