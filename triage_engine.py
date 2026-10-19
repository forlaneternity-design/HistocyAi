import torch
import torch.nn as nn
import torchvision.models as models
from typing import Tuple

class ChromosomeAnomalyTriage(nn.Module):
    def __init__(self, num_classes: int = 2) -> None:
        super(ChromosomeAnomalyTriage, self).__init__()
        self.backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()
        
        self.classifier = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
        
        self.box_regressor = nn.Sequential(
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.Linear(256, 4),
            nn.Sigmoid()
        )
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        features = self.backbone(x)
        logits = self.classifier(features)
        bbox = self.box_regressor(features)
        return logits, bbox

def untangle_chromosome_mask(cluster_mask: torch.Tensor) -> torch.Tensor:
    if not isinstance(cluster_mask, torch.Tensor):
        raise TypeError("Input cluster mask must be a PyTorch Tensor.")
    try:
        isolated_layers = (cluster_mask == 1).float() * 0.5 
        return isolated_layers
    except Exception as e:
        raise RuntimeError(f"Failed during mask decoupling: {str(e)}")
