#!/bin/bash
#SBATCH --job-name=af3_demo6_all
#SBATCH --partition=gpu_h100_4
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=100GB
#SBATCH --time=24:00:00
#SBATCH --array=0-18
#SBATCH --output=af3_demo6_%A_%a.out
#SBATCH --error=af3_demo6_%A_%a.err

# Job-array index -> amino-acid letter for the Q74 mutation.
# Submitting this one script with `sbatch alphafold3_demo6_all.slurm` queues
# all 19 demo6<X>.json runs as a single job array; each array task gets its
# own GPU allocation and runs independently.
AAS=(A R N D C E G H I L K M F P S T W Y V)
AA=${AAS[$SLURM_ARRAY_TASK_ID]}

echo "=========================================="
echo "Job Name: af3_demo6_${AA}"
echo "Array Job ID: ${SLURM_ARRAY_JOB_ID}  Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "Node: $(hostname)"
echo "Partition: gpu_h100_4"
echo "Start Time: $(date)"
echo "=========================================="

module load singularity 2>/dev/null || true

INPUT_DIR=~/af3_input
OUTPUT_DIR=~/af3_output
DB_DIR=~/alphafold3/alphafold3_databases
PARAMS_DIR=~/alphafold3/alphafold3_model_params
SIF_FILE=~/alphafold3/alphafold3.sif

mkdir -p ${OUTPUT_DIR}

echo "Configuration:"
echo "  Input JSON: ${INPUT_DIR}/demo6${AA}.json"
echo "  Output Dir: ${OUTPUT_DIR}"
echo "  Database Dir: ${DB_DIR}"
echo "  Parameters Dir: ${PARAMS_DIR}"
echo "  Container: ${SIF_FILE}"
echo "=========================================="

echo "Starting AlphaFold3 prediction for demo6${AA}..."
singularity run \
  --nv \
  --bind ${INPUT_DIR}:/input \
  --bind ${OUTPUT_DIR}:/output \
  --bind ${DB_DIR}:/databases \
  --bind ${PARAMS_DIR}:/params \
  ${SIF_FILE} \
  python /app/alphafold/run_alphafold.py \
  --json_path=/input/demo6${AA}.json \
  --model_dir=/params \
  --db_dir=/databases \
  --output_dir=/output

EXIT_CODE=$?
echo "=========================================="
if [ ${EXIT_CODE} -eq 0 ]; then
    echo "SUCCESS: demo6${AA} completed"
    echo "End Time: $(date)"
else
    echo "FAILED: demo6${AA} exited with code ${EXIT_CODE}"
    echo "End Time: $(date)"
    exit ${EXIT_CODE}
fi
echo "=========================================="
