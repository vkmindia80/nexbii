import api from './api';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { saveAs } from 'file-saver';

class ExportService {
  // Export query results to CSV
  async exportQueryToCSV(queryId: string): Promise<void> {
    try {
      const response = await api.get(`/api/exports/query/${queryId}/csv`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'text/csv' });
      const filename = this.getFilenameFromResponse(response) || `query_${queryId}.csv`;
      saveAs(blob, filename);
    } catch (error) {
      console.error('CSV export failed:', error);
      throw error;
    }
  }

  // Export query results to Excel
  async exportQueryToExcel(queryId: string): Promise<void> {
    try {
      const response = await api.get(`/api/exports/query/${queryId}/excel`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const filename = this.getFilenameFromResponse(response) || `query_${queryId}.xlsx`;
      saveAs(blob, filename);
    } catch (error) {
      console.error('Excel export failed:', error);
      throw error;
    }
  }

  // Export dashboard configuration to JSON
  async exportDashboardToJSON(dashboardId: string): Promise<void> {
    try {
      const response = await api.get(`/api/exports/dashboard/${dashboardId}/json`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/json' });
      const filename = this.getFilenameFromResponse(response) || `dashboard_${dashboardId}.json`;
      saveAs(blob, filename);
    } catch (error) {
      console.error('JSON export failed:', error);
      throw error;
    }
  }

  // Export dashboard to PDF (backend)
  async exportDashboardToPDF(dashboardId: string): Promise<void> {
    try {
      const response = await api.post(`/api/exports/dashboard/${dashboardId}/pdf`, {}, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const filename = this.getFilenameFromResponse(response) || `dashboard_${dashboardId}.pdf`;
      saveAs(blob, filename);
    } catch (error) {
      console.error('PDF export failed:', error);
      throw error;
    }
  }

  // Export dashboard to PNG (client-side screenshot)
  async exportDashboardToPNG(elementId: string, filename: string = 'dashboard.png'): Promise<void> {
    try {
      const element = document.getElementById(elementId);
      if (!element) {
        throw new Error('Element not found');
      }

      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff'
      });

      canvas.toBlob((blob) => {
        if (blob) {
          saveAs(blob, filename);
        }
      });
    } catch (error) {
      console.error('PNG export failed:', error);
      throw error;
    }
  }

  // Export chart to PNG (client-side)
  async exportChartToPNG(elementId: string, filename: string = 'chart.png'): Promise<void> {
    return this.exportDashboardToPNG(elementId, filename);
  }

  // Export any element as PDF (client-side)
  async exportElementToPDF(
    elementId: string, 
    filename: string = 'export.pdf',
    title?: string
  ): Promise<void> {
    try {
      const element = document.getElementById(elementId);
      if (!element) {
        throw new Error('Element not found');
      }

      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff'
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({
        orientation: canvas.width > canvas.height ? 'landscape' : 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
      const imgX = (pdfWidth - imgWidth * ratio) / 2;
      const imgY = 10;

      if (title) {
        pdf.setFontSize(16);
        pdf.text(title, pdfWidth / 2, 10, { align: 'center' });
      }

      pdf.addImage(
        imgData, 
        'PNG', 
        imgX, 
        title ? imgY + 10 : imgY, 
        imgWidth * ratio, 
        imgHeight * ratio
      );

      pdf.save(filename);
    } catch (error) {
      console.error('PDF export failed:', error);
      throw error;
    }
  }

  // Helper to extract filename from response headers
  private getFilenameFromResponse(response: any): string | null {
    const contentDisposition = response.headers['content-disposition'];
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
      if (filenameMatch && filenameMatch[1]) {
        return filenameMatch[1];
      }
    }
    return null;
  }
}

export default new ExportService();