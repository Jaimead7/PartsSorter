ALTER TABLE images
ADD COLUMN true_result character varying COLLATE pg_catalog."default";

ALTER TABLE images
ADD CONSTRAINT images_true_result_fkey
FOREIGN KEY (true_result)
REFERENCES public.inspection_results (name)
MATCH SIMPLE
ON UPDATE NO ACTION
ON DELETE SET NULL;
