#!/bin/bash
#SBATCH --job-name=af3_demo7Y
#SBATCH --partition=gpu_h100_4
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=100GB
#SBATCH --time=24:00:00
#SBATCH --output=af3_demo7Y_%j.out
#SBATCH --error=af3_demo7Y_%j.err

# Print job information
echo "=========================================="
echo "Job Name: af3_demo7Y"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
echo "Partition: gpu_h100_4"
echo "Start Time: $(date)"
echo "=========================================="

# Load required modules (if needed)
module load singularity 2>/dev/null || true

# Set paths
INPUT_DIR=~/af3_input
OUTPUT_DIR=~/af3_output
DB_DIR=~/alphafold3/alphafold3_databases
PARAMS_DIR=~/alphafold3/alphafold3_model_params
SIF_FILE=~/alphafold3/alphafold3.sif

# Create output directory if it doesn't exist
mkdir -p ${OUTPUT_DIR}

# Print configuration
echo "Configuration:"
echo "  Input JSON: ${INPUT_DIR}/demo7Y.json"
echo "  Output Dir: ${OUTPUT_DIR}"
echo "  Database Dir: ${DB_DIR}"
echo "  Parameters Dir: ${PARAMS_DIR}"
echo "  Container: ${SIF_FILE}"
echo "=========================================="

# Run AlphaFold3
echo "Starting AlphaFold3 prediction..."
singularity run \
  --nv \
  --bind ${INPUT_DIR}:/input \
  --bind ${OUTPUT_DIR}:/output \
  --bind ${DB_DIR}:/databases \
  --bind ${PARAMS_DIR}:/params \
  ${SIF_FILE} \
  python /app/alphafold/run_alphafold.py \
  --json_path=/input/demo7Y.json \
  --model_dir=/params \
  --db_dir=/databases \
  --output_dir=/output

# Check exit status
EXIT_CODE=$?
echo "=========================================="
if [ ${EXIT_CODE} -eq 0 ]; then
    echo "SUCCESS: AlphaFold3 prediction completed"
    echo "End Time: $(date)"
    echo "Output files are in: ${OUTPUT_DIR}"
else
    echo "FAILED: AlphaFold3 prediction failed with exit code ${EXIT_CODE}"
    echo "End Time: $(date)"
    exit ${EXIT_CODE}
fi
echo "=========================================="
