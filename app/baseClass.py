from abc import ABC, abstractmethod


class CTRL(ABC):
    @abstractmethod
    def browse_file(self):
        pass

    @abstractmethod
    def btn_table_click(self):
        pass

    @abstractmethod
    def btn_report_click(self):
        pass

    @abstractmethod
    def btn_export_click(self):
        pass

    @abstractmethod
    def btn_dashboard_click(self):
        pass


class BasePDF(ABC):
    @abstractmethod
    def firstPage(self):
        pass

    @abstractmethod
    def nextPagesHeader(self):
        pass

    @abstractmethod
    def create_graph_contributor(self):
        pass

    @abstractmethod
    def create_graph_details(self):
        pass

    @abstractmethod
    def create_table_dh_open(self):
        pass
