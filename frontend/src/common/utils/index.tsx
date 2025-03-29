import { isEmpty } from 'lodash';

export const isClearable = (selectedItems: any[]) => selectedItems.length > 1;

export const preventDeletion = (
  selectedItems: string[],
  setSelected: Function,
) => {
  return (e: any) => {
    if (isEmpty(e) && selectedItems.length === 1) return;
    if (e.length < 1) {
      setSelected([selectedItems[0]]);
      return;
    }
    setSelected(e ? e.map((option: any) => option.value) : []);
  };
};

export const getMinMaxValues = (data: number[]) => {
  const min = Math.min(...data);
  const max = Math.max(...data);
  return { min, max: max + 10 };
};
