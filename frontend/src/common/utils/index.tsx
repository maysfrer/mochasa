import { isEmpty } from 'lodash';

// Allow clearing only if more than 1 item is selected, unless allowClearAll is true
export const isClearable = (selectedItems: any[], allowClearAll = false) =>
  allowClearAll || selectedItems.length > 1;

export const preventDeletion = (
  selectedItems: string[],
  setSelected: Function,
  allowClearAll: boolean = false,
) => {
  return (e: any) => {
    if (isEmpty(e)) {
      if (allowClearAll) {
        setSelected([]); // allow full reset
      } else if (selectedItems.length === 1) {
        return; // prevent full deletion
      }
    } else if (e.length < 1 && !allowClearAll) {
      setSelected([selectedItems[0]]);
    } else {
      setSelected(e.map((option: any) => option.value));
    }
  };
};

export const getMinMaxValues = (data: number[]) => {
  const min = Math.min(...data);
  const max = Math.max(...data);
  return { min, max: max + 10 };
};
